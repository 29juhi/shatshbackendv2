from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime, timedelta
import random

from database import get_db, create_tables
from models import User, SavedPost, Reminder, ChatMessage, PlatformEnum
from schemas import (
    UserCreate, User as UserSchema,
    SavedPostCreate, SavedPost as SavedPostSchema, SavedPostsResponse,
    ReminderCreate, ReminderUpdate, Reminder as ReminderSchema,
    ChatMessageCreate, ChatMessage as ChatMessageSchema, ChatResponse
)

# Create FastAPI app
app = FastAPI(title="Stash API", description="Backend for Stash content management app")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Helper function to get current user (simplified for demo)
def get_current_user(db: Session = Depends(get_db)) -> User:
    # In a real app, you'd validate JWT token here
    user = db.query(User).first()
    if not user:
        # Create a demo user if none exists
        user = User(email="demo@example.com", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# User endpoints
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# SavedPost endpoints
@app.get("/saved-posts/", response_model=SavedPostsResponse)
def get_saved_posts(
    skip: int = 0, 
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SavedPost).filter(SavedPost.user_id == current_user.id)
    
    if category and category != "All":
        query = query.filter(SavedPost.tags.contains(category))
    
    posts = query.offset(skip).limit(limit).all()
    total = query.count()
    
    # Convert tags from JSON string to list
    for post in posts:
        if post.tags:
            post.tags = json.loads(post.tags) if isinstance(post.tags, str) else post.tags
    
    # Calculate stats
    stats = {
        "total_items": total,
        "active_reminders": db.query(Reminder).filter(
            Reminder.user_id == current_user.id,
            Reminder.is_completed == False
        ).count(),
        "completed_items": db.query(Reminder).filter(
            Reminder.user_id == current_user.id,
            Reminder.is_completed == True
        ).count()
    }
    
    return SavedPostsResponse(posts=posts, total=total, stats=stats)

@app.post("/saved-posts/", response_model=SavedPostSchema)
def create_saved_post(
    post: SavedPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Convert tags list to JSON string for storage
    post_data = post.dict()
    post_data["tags"] = json.dumps(post_data["tags"])
    post_data["user_id"] = current_user.id
    
    # Simple AI detection simulation
    ai_keywords = ["job", "hiring", "opportunity", "scholarship", "deadline", "apply"]
    post_data["ai_detected"] = any(keyword in post.title.lower() or keyword in post.summary.lower() 
                                   for keyword in ai_keywords)
    
    db_post = SavedPost(**post_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Convert back to list for response
    db_post.tags = json.loads(db_post.tags)
    return db_post

@app.delete("/saved-posts/{post_id}")
def delete_saved_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(SavedPost).filter(
        SavedPost.id == post_id,
        SavedPost.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}

# Reminder endpoints
@app.get("/reminders/", response_model=List[ReminderSchema])
def get_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Reminder).filter(Reminder.user_id == current_user.id).all()

@app.post("/reminders/", response_model=ReminderSchema)
def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reminder = Reminder(**reminder.dict(), user_id=current_user.id)
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.put("/reminders/{reminder_id}", response_model=ReminderSchema)
def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    for field, value in reminder_update.dict(exclude_unset=True).items():
        setattr(reminder, field, value)
    
    db.commit()
    db.refresh(reminder)
    return reminder

@app.delete("/reminders/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted successfully"}

# Chat endpoints
@app.get("/chat/messages/", response_model=List[ChatMessageSchema])
def get_chat_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.timestamp).all()

@app.post("/chat/send/", response_model=ChatResponse)
def send_chat_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Save user message
    user_message = ChatMessage(
        user_id=current_user.id,
        message=message.message,
        is_user=True
    )
    db.add(user_message)
    db.commit()
    
    # Generate AI response (simplified)
    ai_responses = [
        f"I understand you're asking about '{message.message}'. Let me help you find relevant saved content.",
        f"Based on your query about '{message.message}', I can help you organize your saved posts or set up reminders.",
        "That's an interesting question! I can help you manage your saved content more effectively.",
        "I'm here to help you with your saved posts and reminders. What specific assistance do you need?",
        f"Regarding '{message.message}', I can help you categorize your content or create relevant reminders."
    ]
    
    ai_response_text = random.choice(ai_responses)
    
    # Save AI response
    ai_message = ChatMessage(
        user_id=current_user.id,
        message=ai_response_text,
        is_user=False
    )
    db.add(ai_message)
    db.commit()
    
    return ChatResponse(message=ai_response_text, timestamp=ai_message.timestamp)

# Analytics endpoint
@app.get("/analytics/")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get posts by platform
    posts_by_platform = {}
    for platform in PlatformEnum:
        count = db.query(SavedPost).filter(
            SavedPost.user_id == current_user.id,
            SavedPost.platform == platform
        ).count()
        posts_by_platform[platform.value] = count
    
    # Get posts by tags
    posts = db.query(SavedPost).filter(SavedPost.user_id == current_user.id).all()
    tags_count = {}
    for post in posts:
        if post.tags:
            tags = json.loads(post.tags) if isinstance(post.tags, str) else post.tags
            for tag in tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
    
    # Upcoming deadlines
    upcoming_deadlines = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.due_date > datetime.utcnow(),
        Reminder.is_completed == False
    ).order_by(Reminder.due_date).limit(5).all()
    
    return {
        "posts_by_platform": posts_by_platform,
        "posts_by_tags": tags_count,
        "upcoming_deadlines": len(upcoming_deadlines),
        "total_posts": len(posts),
        "ai_detected_posts": sum(1 for post in posts if post.ai_detected),
        "active_reminders": db.query(Reminder).filter(
            Reminder.user_id == current_user.id,
            Reminder.is_completed == False
        ).count(),
        "completed_reminders": db.query(Reminder).filter(
            Reminder.user_id == current_user.id,
            Reminder.is_completed == True
        ).count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
