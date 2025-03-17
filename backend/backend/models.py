import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ConversationState(enum.Enum):
    NEW = "new"
    ENGAGED = "engaged"
    BOOKED = "booked"
    OPTED_OUT = "opted_out"
    UNRESPONSIVE = "unresponsive"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    additional_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    conversations = relationship("Conversation", back_populates="lead")

    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', phone='{self.phone_number}')>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    state = Column(String(20), default=ConversationState.NEW.value)
    last_contact = Column(DateTime, nullable=True)
    booking_link_sent = Column(Boolean, default=False)
    booking_link_clicked = Column(Boolean, default=False)
    booking_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

    def __repr__(self):
        return f"<Conversation(id={self.id}, lead_id={self.lead_id}, state='{self.state}')>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_from_lead = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivered = Column(Boolean, default=False)
    delivery_error = Column(Text, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, from_lead={self.is_from_lead}, content='{self.content[:20]}...')>"
