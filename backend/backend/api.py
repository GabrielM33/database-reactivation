import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.csv_processor import CSVProcessor
from backend.database import get_db, init_db
from backend.llm_engine import LLMConversationEngine
from backend.models import Conversation, ConversationState, Lead, Message
from backend.sms_gateway import SMSGateway
from backend.state_manager import StateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API
app = FastAPI(title="Database Reactivation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM and SMS gateway
llm_engine = LLMConversationEngine()
sms_gateway = SMSGateway(llm_engine=llm_engine)

# Initialize state manager (will be created per request)
state_manager = None


# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")


# Endpoints
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Database Reactivation API"}


@app.post("/import-leads")
async def import_leads(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Import leads from a CSV file."""
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        # Process the file in the background
        background_tasks.add_task(process_import_file, temp_path, db)

        return {
            "status": "processing",
            "message": "CSV file upload received. Import is being processed in the background.",
        }

    except Exception as e:
        logger.error(f"Error importing leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.get("/leads")
def get_leads(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get a list of leads, optionally filtered by conversation state."""
    try:
        query = db.query(Lead)

        if state:
            # Filter by conversation state
            query = query.join(Lead.conversations).filter(Conversation.state == state)

        total = query.count()
        leads = query.offset(skip).limit(limit).all()

        # Format the leads data
        lead_data = []
        for lead in leads:
            lead_dict = {
                "id": lead.id,
                "name": lead.name,
                "phone_number": lead.phone_number,
                "email": lead.email,
                "created_at": lead.created_at.isoformat(),
                "updated_at": lead.updated_at.isoformat(),
            }

            # Get the latest conversation state
            if lead.conversations:
                latest_conversation = max(
                    lead.conversations, key=lambda c: c.updated_at
                )
                lead_dict["conversation_state"] = latest_conversation.state
                lead_dict["last_contact"] = (
                    latest_conversation.last_contact.isoformat()
                    if latest_conversation.last_contact
                    else None
                )

            lead_data.append(lead_dict)

        return {"total": total, "leads": lead_data}

    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get leads: {str(e)}")


@app.get("/conversations")
def get_conversations(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = None,
    lead_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get a list of conversations, optionally filtered by state or lead ID."""
    try:
        query = db.query(Conversation)

        if state:
            query = query.filter(Conversation.state == state)

        if lead_id:
            query = query.filter(Conversation.lead_id == lead_id)

        total = query.count()
        conversations = query.offset(skip).limit(limit).all()

        # Format the conversations data
        conversation_data = []
        for conv in conversations:
            conv_dict = {
                "id": conv.id,
                "lead_id": conv.lead_id,
                "lead_name": conv.lead.name if conv.lead else None,
                "state": conv.state,
                "last_contact": (
                    conv.last_contact.isoformat() if conv.last_contact else None
                ),
                "booking_link_sent": conv.booking_link_sent,
                "booking_completed": conv.booking_completed,
                "message_count": len(conv.messages),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }

            conversation_data.append(conv_dict)

        return {"total": total, "conversations": conversation_data}

    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversations: {str(e)}"
        )


@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages for a specific conversation."""
    try:
        conversation = (
            db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )
        if not conversation:
            raise HTTPException(
                status_code=404, detail=f"Conversation {conversation_id} not found"
            )

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at)
            .all()
        )

        # Format the messages data
        message_data = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "content": msg.content,
                "is_from_lead": msg.is_from_lead,
                "sent_at": msg.sent_at.isoformat(),
                "delivered": msg.delivered,
            }

            message_data.append(msg_dict)

        return {
            "conversation_id": conversation_id,
            "lead_name": conversation.lead.name if conversation.lead else None,
            "state": conversation.state,
            "messages": message_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@app.post("/send-message")
async def send_message(
    lead_id: int = Form(...), message: str = Form(...), db: Session = Depends(get_db)
):
    """Send a manual message to a lead."""
    try:
        # Get the lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")

        # Get or create a conversation for this lead
        conversation = (
            db.query(Conversation)
            .filter(Conversation.lead_id == lead_id)
            .order_by(Conversation.created_at.desc())
            .first()
        )

        if not conversation:
            conversation = Conversation(
                lead_id=lead_id, state=ConversationState.ENGAGED.value
            )
            db.add(conversation)
            db.commit()

        # Send the message
        result = sms_gateway.send_message(
            to_number=lead.phone_number,
            content=message,
            conversation_id=conversation.id,
            db=db,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=f"Failed to send message: {result['error']}"
            )

        return {
            "status": "sent",
            "message_id": result["message_id"],
            "conversation_id": conversation.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@app.post("/webhook/twilio")
async def twilio_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming Twilio webhook."""
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        request_data = dict(form_data)

        # Handle the webhook
        result = sms_gateway.handle_twilio_webhook(request_data, db)

        if not result["success"]:
            logger.error(f"Webhook processing failed: {result.get('error')}")
            return {"status": "error", "message": result.get("error")}

        return {"status": "success", "message": "Webhook processed successfully"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/start-scheduler")
async def start_scheduler(
    background_tasks: BackgroundTasks,
    max_concurrent: int = Form(50),
    messages_per_minute: int = Form(10),
    db: Session = Depends(get_db),
):
    """Start the conversation scheduler."""
    global state_manager

    try:
        # Create a new state manager if needed
        if not state_manager:
            state_manager = StateManager(
                db_session=db,
                llm_engine=llm_engine,
                sms_gateway=sms_gateway,
                max_concurrent_conversations=max_concurrent,
                messages_per_minute=messages_per_minute,
            )

        # Start the scheduler in the background
        background_tasks.add_task(run_scheduler, state_manager)

        return {"status": "started", "message": "Conversation scheduler started"}

    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start scheduler: {str(e)}"
        )


@app.post("/stop-scheduler")
def stop_scheduler():
    """Stop the conversation scheduler."""
    global state_manager

    try:
        if state_manager:
            state_manager.stop_scheduler()
            return {"status": "stopped", "message": "Conversation scheduler stopped"}
        else:
            return {"status": "not_running", "message": "Scheduler was not running"}

    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop scheduler: {str(e)}"
        )


@app.post("/export-leads")
async def export_leads(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Export all leads to a CSV file."""
    try:
        # Create a temporary file for the export
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        temp_path = temp_file.name
        temp_file.close()

        # Process the export in the background
        background_tasks.add_task(process_export_file, temp_path, db)

        return {
            "status": "processing",
            "message": "Export is being processed in the background. The file will be available for download soon.",
            "file_path": temp_path,
        }

    except Exception as e:
        logger.error(f"Error exporting leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Background task functions
async def process_import_file(file_path: str, db: Session):
    """Process the imported CSV file in the background."""
    try:
        # Import the leads
        results = CSVProcessor.import_leads(file_path, db)

        logger.info(f"Import completed: {json.dumps(results)}")

        # Delete the temporary file
        os.unlink(file_path)

    except Exception as e:
        logger.error(f"Error processing import file: {str(e)}")

        # Make sure to delete the temporary file
        if os.path.exists(file_path):
            os.unlink(file_path)


async def process_export_file(file_path: str, db: Session):
    """Process the export in the background."""
    try:
        # Export the leads
        exported_count = CSVProcessor.export_leads(db, file_path)

        logger.info(f"Export completed: {exported_count} leads exported to {file_path}")

    except Exception as e:
        logger.error(f"Error processing export: {str(e)}")

        # Make sure to delete the temporary file if there was an error
        if os.path.exists(file_path):
            os.unlink(file_path)


async def run_scheduler(state_manager: StateManager):
    """Run the conversation scheduler in the background."""
    try:
        await state_manager.start_scheduler()
    except Exception as e:
        logger.error(f"Error running scheduler: {str(e)}")
