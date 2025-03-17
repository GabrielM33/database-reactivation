import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from backend.models import Conversation, ConversationState, Lead, Message

logger = logging.getLogger(__name__)


class LLMConversationEngine:
    """
    LLM-powered engine for generating contextual messages and managing conversations.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        """Initialize the LLM conversation engine."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key)
        self.booking_link = os.getenv(
            "BOOKING_LINK", "https://calendly.com/example/sales-call"
        )

    def _get_conversation_context(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Prepare the conversation context for LLM prompting.
        """
        lead = conversation.lead
        messages = conversation.messages

        # Format message history
        message_history = []
        for msg in messages:
            role = "user" if msg.is_from_lead else "assistant"
            message_history.append({"role": role, "content": msg.content})

        # Prepare lead information
        lead_info = {
            "name": lead.name,
            "phone": lead.phone_number,
            "email": lead.email,
            "additional_info": lead.additional_info,
        }

        # Prepare conversation state
        conversation_state = {
            "state": conversation.state,
            "last_contact": (
                conversation.last_contact.isoformat()
                if conversation.last_contact
                else None
            ),
            "booking_link_sent": conversation.booking_link_sent,
            "booking_link_clicked": conversation.booking_link_clicked,
            "booking_completed": conversation.booking_completed,
            "message_count": len(messages),
        }

        return {
            "lead": lead_info,
            "conversation_state": conversation_state,
            "message_history": message_history,
        }

    def _prepare_system_prompt(self, conversation_context: Dict[str, Any]) -> str:
        """
        Prepare the system prompt based on the conversation context.
        """
        lead = conversation_context["lead"]
        state = conversation_context["conversation_state"]
        booking_link = self.booking_link

        system_prompt = f"""
        You are an AI assistant managing SMS conversations with potential leads for a business. 
        Your goal is to engage the lead in a friendly conversation and ultimately encourage them to book a sales call.
        
        Lead Information:
        - Name: {lead['name']}
        - Additional Info: {lead['additional_info'] or 'None provided'}
        
        Conversation State:
        - Current State: {state['state']}
        - Messages Exchanged: {state['message_count']}
        - Booking Link Sent: {"Yes" if state['booking_link_sent'] else "No"}
        - Booking Completed: {"Yes" if state['booking_completed'] else "No"}
        
        Booking Link: {booking_link}
        
        Guidelines:
        1. Be friendly, professional, and concise - remember this is SMS.
        2. Keep messages under 160 characters when possible.
        3. Use the lead's name at appropriate times.
        4. Recognize when the lead is asking questions and answer helpfully.
        5. Share the booking link when the lead shows interest or asks how to proceed.
        6. Respect opt-out requests and acknowledge them politely.
        7. Don't be pushy but guide the conversation toward booking a call.
        8. If the lead says they've booked a call, express gratitude and confirm.
        
        If you determine that sharing the booking link is appropriate, include it in your response.
        """

        return system_prompt

    def generate_message(self, conversation_id: int, db: Session) -> Optional[str]:
        """
        Generate a contextual message based on the conversation history.
        """
        # Get conversation and related data
        conversation = (
            db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return None

        # Get context
        context = self._get_conversation_context(conversation)

        # Check if we need to update conversation state
        self._update_conversation_state(conversation, context, db)

        # Don't generate messages for completed or opted-out conversations
        if conversation.state in [
            ConversationState.BOOKED.value,
            ConversationState.OPTED_OUT.value,
        ]:
            logger.info(
                f"Skipping message generation for {conversation.state} conversation {conversation_id}"
            )
            return None

        # Prepare prompts
        system_prompt = self._prepare_system_prompt(context)

        messages = [{"role": "system", "content": system_prompt}]

        # Add message history
        for msg in context["message_history"]:
            messages.append(msg)

        # If this is a new conversation with no messages, add an initial user prompt
        if not context["message_history"]:
            messages.append(
                {
                    "role": "user",
                    "content": "This is a new lead that needs to be contacted. Generate an initial outreach message.",
                }
            )

        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
            )

            # Extract the generated message
            generated_message = response.choices[0].message.content.strip()

            # Check if booking link is included and update conversation state
            if (
                self.booking_link in generated_message
                and not conversation.booking_link_sent
            ):
                conversation.booking_link_sent = True
                db.commit()

            return generated_message

        except Exception as e:
            logger.error(f"Error generating message: {str(e)}")
            return None

    def _update_conversation_state(
        self, conversation: Conversation, context: Dict[str, Any], db: Session
    ) -> None:
        """
        Update the conversation state based on the conversation context.
        """
        # Check for opt-out keywords in the last user message
        if (
            context["message_history"]
            and context["message_history"][-1]["role"] == "user"
        ):
            last_message = context["message_history"][-1]["content"].lower()
            opt_out_keywords = [
                "stop",
                "unsubscribe",
                "opt out",
                "don't text",
                "don't message",
            ]

            if any(keyword in last_message for keyword in opt_out_keywords):
                conversation.state = ConversationState.OPTED_OUT.value
                db.commit()
                return

            # Check for booking confirmation
            booking_keywords = [
                "booked",
                "scheduled",
                "appointment",
                "meeting",
                "call scheduled",
            ]
            if any(keyword in last_message for keyword in booking_keywords):
                conversation.state = ConversationState.BOOKED.value
                conversation.booking_completed = True
                db.commit()
                return

        # Update state based on message count and engagement
        message_count = len(conversation.messages)

        if message_count > 0 and conversation.state == ConversationState.NEW.value:
            conversation.state = ConversationState.ENGAGED.value

        # Check for unresponsive leads
        if conversation.last_contact:
            days_since_contact = (datetime.utcnow() - conversation.last_contact).days
            if (
                days_since_contact > 3
                and conversation.state == ConversationState.ENGAGED.value
            ):
                conversation.state = ConversationState.UNRESPONSIVE.value

        db.commit()

    def process_incoming_message(
        self, phone_number: str, message_content: str, db: Session
    ) -> Dict[str, Any]:
        """
        Process an incoming message from a lead.

        Returns a dictionary with:
        - success: boolean indicating success
        - conversation_id: ID of the conversation
        - response: Generated response (if any)
        - error: Error message (if any)
        """
        result = {
            "success": False,
            "conversation_id": None,
            "response": None,
            "error": None,
        }

        try:
            # Find the lead by phone number
            lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
            if not lead:
                result["error"] = f"Lead not found for phone number {phone_number}"
                return result

            # Find or create conversation
            conversation = (
                db.query(Conversation)
                .filter(Conversation.lead_id == lead.id)
                .order_by(Conversation.created_at.desc())
                .first()
            )

            if not conversation:
                conversation = Conversation(
                    lead_id=lead.id, state=ConversationState.NEW.value
                )
                db.add(conversation)
                db.commit()

            result["conversation_id"] = conversation.id

            # Add the message to the conversation
            message = Message(
                conversation_id=conversation.id,
                content=message_content,
                is_from_lead=True,
                delivered=True,
            )
            db.add(message)

            # Update conversation last_contact time
            conversation.last_contact = datetime.utcnow()
            db.commit()

            # Generate a response
            response = self.generate_message(conversation.id, db)

            if response:
                # Save the response
                response_message = Message(
                    conversation_id=conversation.id,
                    content=response,
                    is_from_lead=False,
                )
                db.add(response_message)
                db.commit()

                result["response"] = response

            result["success"] = True
            return result

        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
            result["error"] = str(e)
            return result
