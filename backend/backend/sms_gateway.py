import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from backend.llm_engine import LLMConversationEngine
from backend.models import Conversation, Message

logger = logging.getLogger(__name__)


class SMSGateway:
    """
    Handles sending and receiving SMS messages using Twilio.
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        llm_engine: Optional[LLMConversationEngine] = None,
    ):
        """Initialize the SMS gateway."""
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials and phone number are required")

        self.client = Client(self.account_sid, self.auth_token)
        self.llm_engine = llm_engine

    def send_message(
        self, to_number: str, content: str, conversation_id: int, db: Session
    ) -> Dict[str, Any]:
        """
        Send an SMS message to a lead and record it in the database.
        """
        result = {
            "success": False,
            "message_id": None,
            "error": None,
            "twilio_sid": None,
        }

        try:
            # Get conversation
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if not conversation:
                result["error"] = f"Conversation {conversation_id} not found"
                return result

            # Create message record
            message = Message(
                conversation_id=conversation_id,
                content=content,
                is_from_lead=False,
                sent_at=datetime.utcnow(),
            )
            db.add(message)
            db.commit()

            result["message_id"] = message.id

            # Send message via Twilio
            twilio_message = self.client.messages.create(
                body=content, from_=self.from_number, to=to_number
            )

            # Update message with Twilio SID
            message.delivered = True
            message.delivery_error = None
            db.commit()

            result["success"] = True
            result["twilio_sid"] = twilio_message.sid

            # Update conversation last_contact time
            conversation.last_contact = datetime.utcnow()
            db.commit()

            return result

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {str(e)}")

            if message:
                message.delivered = False
                message.delivery_error = str(e)
                db.commit()

            result["error"] = str(e)
            return result

        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")

            if message:
                message.delivered = False
                message.delivery_error = str(e)
                db.commit()

            result["error"] = str(e)
            return result

    def receive_message(
        self, from_number: str, content: str, db: Session
    ) -> Dict[str, Any]:
        """
        Process an incoming SMS message from a lead.
        """
        if not self.llm_engine:
            raise ValueError("LLM engine is required to process incoming messages")

        # Process the message with the LLM engine
        result = self.llm_engine.process_incoming_message(from_number, content, db)

        # If there's a response to send back, send it
        if result["success"] and result["response"]:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == result["conversation_id"])
                .first()
            )
            if conversation and conversation.lead:
                self.send_message(
                    to_number=conversation.lead.phone_number,
                    content=result["response"],
                    conversation_id=result["conversation_id"],
                    db=db,
                )

        return result

    def handle_twilio_webhook(
        self, request_data: Dict[str, Any], db: Session
    ) -> Dict[str, Any]:
        """
        Handle incoming webhook from Twilio.
        """
        try:
            # Extract message details from Twilio webhook payload
            from_number = request_data.get("From")
            body = request_data.get("Body")
            message_sid = request_data.get("MessageSid")

            if not all([from_number, body, message_sid]):
                return {
                    "success": False,
                    "error": "Missing required data in webhook payload",
                }

            # Process the incoming message
            result = self.receive_message(from_number, body, db)

            return {
                "success": True,
                "message_sid": message_sid,
                "processed": result["success"],
            }

        except Exception as e:
            logger.error(f"Error handling Twilio webhook: {str(e)}")
            return {"success": False, "error": str(e)}
