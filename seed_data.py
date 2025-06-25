from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from models import User, SavedPost, Reminder, ChatMessage, PlatformEnum
import json
from datetime import datetime, timedelta

def seed_database():
    create_tables()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already seeded!")
            return
        
        # Create demo user
        user = User(
            email="demo@stashapp.com",
            name="Demo User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create sample saved posts
        sample_posts = [
            {
                "platform": PlatformEnum.LINKEDIN,
                "title": "Senior React Developer at Tech Corp",
                "summary": "Remote position with competitive salary and great benefits",
                "tags": json.dumps(["Job", "React", "Remote"]),
                "ai_detected": True,
                "has_deadline": True,
                "deadline": datetime.utcnow() + timedelta(days=7)
            },
            {
                "platform": PlatformEnum.INSTAGRAM,
                "title": "48-Hour Code Challenge Starting Soon",
                "summary": "Build the next big thing in tech with amazing prizes",
                "tags": json.dumps(["Hackathon", "Coding"]),
                "ai_detected": True,
                "has_deadline": True,
                "deadline": datetime.utcnow() + timedelta(days=3)
            },
            {
                "platform": PlatformEnum.YOUTUBE,
                "title": "Full Scholarship Program for CS Students",
                "summary": "Apply now for full tuition coverage at top universities",
                "tags": json.dumps(["Scholarship", "Education"]),
                "ai_detected": False,
                "has_deadline": True,
                "deadline": datetime.utcnow() + timedelta(days=30)
            },
            {
                "platform": PlatformEnum.TWITTER,
                "title": "Machine Learning Study Group",
                "summary": "Join our weekly ML study sessions and projects",
                "tags": json.dumps(["Study", "ML", "Group"]),
                "ai_detected": False,
                "has_deadline": False
            },
            {
                "platform": PlatformEnum.LINKEDIN,
                "title": "Tech Conference 2024 - Early Bird Registration",
                "summary": "Don't miss the biggest tech event of the year",
                "tags": json.dumps(["Events", "Conference", "Tech"]),
                "ai_detected": True,
                "has_deadline": True,
                "deadline": datetime.utcnow() + timedelta(days=14)
            }
        ]
        
        for post_data in sample_posts:
            post = SavedPost(user_id=user.id, **post_data)
            db.add(post)
        
        # Create sample reminders
        sample_reminders = [
            {
                "title": "Google Summer of Code Application",
                "description": "Submit application for GSoC 2024 program",
                "due_date": datetime.utcnow() + timedelta(days=15),
                "is_urgent": True
            },
            {
                "title": "Tech Conference Registration",
                "description": "Register for the annual tech conference",
                "due_date": datetime.utcnow() + timedelta(days=30),
                "is_urgent": False
            },
            {
                "title": "Portfolio Update",
                "description": "Update portfolio with recent projects",
                "due_date": datetime.utcnow() + timedelta(days=7),
                "is_urgent": False
            },
            {
                "title": "Scholarship Essay Submission",
                "description": "Complete and submit scholarship essay",
                "due_date": datetime.utcnow() + timedelta(days=21),
                "is_urgent": True
            }
        ]
        
        for reminder_data in sample_reminders:
            reminder = Reminder(user_id=user.id, **reminder_data)
            db.add(reminder)
        
        # Create sample chat messages
        sample_messages = [
            {
                "message": "Hi! I'm your AI assistant. How can I help you manage your saved content today?",
                "is_user": False,
                "timestamp": datetime.utcnow() - timedelta(minutes=30)
            },
            {
                "message": "Can you help me organize my job-related posts?",
                "is_user": True,
                "timestamp": datetime.utcnow() - timedelta(minutes=25)
            },
            {
                "message": "Of course! I can see you have several job-related posts. Would you like me to create reminders for application deadlines?",
                "is_user": False,
                "timestamp": datetime.utcnow() - timedelta(minutes=24)
            }
        ]
        
        for msg_data in sample_messages:
            message = ChatMessage(user_id=user.id, **msg_data)
            db.add(message)
        
        db.commit()
        print("Database seeded successfully!")
        print(f"Created user: {user.email}")
        print(f"Created {len(sample_posts)} saved posts")
        print(f"Created {len(sample_reminders)} reminders")
        print(f"Created {len(sample_messages)} chat messages")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
