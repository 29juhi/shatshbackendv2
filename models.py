from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class PlatformEnum(enum.Enum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    saved_posts = relationship("SavedPost", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

class SavedPost(Base):
    __tablename__ = "saved_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(Enum(PlatformEnum))
    title = Column(String)
    summary = Column(Text)
    tags = Column(String)  # JSON string of tags
    saved_at = Column(DateTime, default=datetime.utcnow)
    has_deadline = Column(Boolean, default=False)
    deadline = Column(DateTime, nullable=True)
    ai_detected = Column(Boolean, default=False)
    original_url = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="saved_posts")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    is_user = Column(Boolean)  # True if from user, False if from AI
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
