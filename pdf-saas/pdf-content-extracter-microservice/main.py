from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import os
import uvicorn
from pdf.extractor import PDFExtractor
from dotenv import load_dotenv

# Loading API and .env
app = FastAPI()
load_dotenv()

# Load route path from .env
PDF_ROUTE = os.getenv("PDF_ROUTE", "/pdf/{start_page}/{end_page}")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
DEFAULT_ROUTE = os.getenv("DEFAULT_ROUTE", "/")
HOST = os.getenv("HOST", "0.0.0.0")  # Default 0.0.0.0 if not set
PORT = int(os.getenv("PORT", 8000))  # Default 8000 if not set

# Configurable upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Health Check for the API
@app.get(DEFAULT_ROUTE)
def root():
    return {"message": "PDF Extraction API is running!"}

# Request for the PDF extract
@app.post(PDF_ROUTE)
async def extract_pdf(
    start_page: int,
    end_page: int,
    file: UploadFile = File(...)
):
    try:
        # Save uploaded PDF
        pdf_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract content using OOP class
        extractor = PDFExtractor(pdf_path)
        content = extractor.extract_content(start_page, end_page)
        
        # Delete PDF after processing (optional)
        os.remove(pdf_path)
        
        # Return extracted content as JSON response
        return JSONResponse(content)

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
