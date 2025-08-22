from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pdf.PDFGenerate import PDFGenerator
from dotenv import load_dotenv
import os, shutil, json
import uvicorn

app = FastAPI()
load_dotenv()

GENERATE_ROUTE = os.getenv("GENERATE_ROUTE", "/generate_pdf")
PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "../STORAGE/pdf")
HOST = os.getenv("HOST", "0.0.0.0")  # Default 0.0.0.0 if not set
PORT = int(os.getenv("PORT", 8003))  # Default 8000 if not set

temp_json_path = "temp/uploaded.json"

@app.post(GENERATE_ROUTE)
async def generate_pdf(uid: str = Form(...), file: UploadFile = None):

    with open(temp_json_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load JSON data
    try:
        with open(temp_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"Invalid JSON file: {str(e)}"}, status_code=400)

    # Create PDF
    pdf_path = f"{PDF_STORAGE_PATH}/{uid}.pdf"
    pdf_gen = PDFGenerator(pdf_path)
    pdf_file_path = pdf_gen.create_pdf(data)

    return {"pdf_file": pdf_file_path}

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
