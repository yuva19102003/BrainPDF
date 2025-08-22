import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from ai.GeminiSummarize import PDFSummarizer

# Loading API and .env
load_dotenv()
app = FastAPI()

# Load values from .env
API_KEY = os.getenv("API_KEY")
AI_ROUTE = os.getenv("AI_ROUTE", "/summarize")
DEFAULT_ROUTE = os.getenv("DEFAULT_ROUTE", "/")
HOST = os.getenv("HOST", "0.0.0.0")  # Default 0.0.0.0 if not set
PORT = int(os.getenv("PORT", 8000))  # Default 8000 if not set

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required.")


class SummarizeRequest(BaseModel):
    content: str

gemini = PDFSummarizer(api_key=API_KEY)

# Health Check for the API
@app.get(DEFAULT_ROUTE)
def root():
    return {"message": "PDF Extraction API is running!"}


@app.post(AI_ROUTE)
def summarize(request: SummarizeRequest):
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="The 'content' field must not be empty.")

    result = gemini.summarize_content(content)
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
