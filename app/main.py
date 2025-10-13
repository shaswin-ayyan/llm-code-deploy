from fastapi import FastAPI
from app.api.v1 import users

# Initialize the FastAPI application
app = FastAPI()

# Include the user-related routes
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}