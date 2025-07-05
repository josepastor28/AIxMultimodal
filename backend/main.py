from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="AIxMultimodal API",
    description="Backend API for AIxMultimodal application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Message(BaseModel):
    id: Optional[int] = None
    content: str
    sender: str
    timestamp: Optional[str] = None

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str

# In-memory storage (replace with database in production)
messages: List[Message] = []
users: List[User] = []

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AIxMultimodal API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AIxMultimodal API"}

@app.get("/api/messages")
async def get_messages():
    """Get all messages"""
    return {"messages": messages}

@app.post("/api/messages")
async def create_message(message: Message):
    """Create a new message"""
    message.id = len(messages) + 1
    messages.append(message)
    return {"message": "Message created successfully", "data": message}

@app.get("/api/users")
async def get_users():
    """Get all users"""
    return {"users": users}

@app.post("/api/users")
async def create_user(user: User):
    """Create a new user"""
    # Check if user already exists
    for existing_user in users:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user.id = len(users) + 1
    users.append(user)
    return {"message": "User created successfully", "data": user}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """Get a specific user by ID"""
    for user in users:
        if user.id == user_id:
            return {"user": user}
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 