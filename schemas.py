from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from models import PlatformEnum

# User schemas
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# SavedPost schemas
class SavedPostBase(BaseModel):
    platform: PlatformEnum
    title: str
    summary: str
    tags: List[str]
    has_deadline: bool = False
    deadline: Optional[datetime] = None
    ai_detected: bool = False
    original_url: Optional[str] = None

class SavedPostCreate(SavedPostBase):
    pass

class SavedPost(SavedPostBase):
    id: int
    user_id: int
    saved_at: datetime
    
    class Config:
        from_attributes = True

# Reminder schemas
class ReminderBase(BaseModel):
    title: str
    description: str
    due_date: datetime
    is_urgent: bool = False

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    is_urgent: Optional[bool] = None

class Reminder(ReminderBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ChatMessage schemas
class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    is_user: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class SavedPostsResponse(BaseModel):
    posts: List[SavedPost]
    total: int
    stats: dict

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime
