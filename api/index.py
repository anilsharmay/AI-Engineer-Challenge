# Vercel entry point for the MS DOS Chatbot API
from app import app
from mangum import Mangum

# Create handler for Vercel
handler = Mangum(app)
