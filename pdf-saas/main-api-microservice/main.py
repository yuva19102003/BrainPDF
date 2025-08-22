from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
import uvicorn
import uuid
import aiofiles
import httpx
import os
import json

app = FastAPI()
load_dotenv()


UPLOAD_ROUTE = os.getenv("UPLOAD_ROUTE", "/upload/{x}/{y}")
GENERATE_ROUTE = os.getenv("GENERATE_ROUTE", "/generate")
HOST = os.getenv("HOST", "0.0.0.0")  # Default 0.0.0.0 if not set
PORT = int(os.getenv("PORT", 8000))  # Default 8000 if not set
PDF_STORAGE = os.getenv("PDF_STORAGE", "../STORAGE/pdf")
JSON_STORAGE = os.getenv("JSON_STORAGE", "../STORAGE/json")
ENDPOINT_1 = os.getenv("ENDPOINT_1", "http://127.0.0.1:8001/pdf/{x}/{y}")
ENDPOINT_2 = os.getenv("ENDPOINT_2", "http://127.0.0.1:8002/summarize")
ENDPOINT_3 = os.getenv("ENDPOINT_3", "http://127.0.0.1:8003/generate_pdf") # endpoint 3

os.makedirs(PDF_STORAGE, exist_ok=True)
os.makedirs(JSON_STORAGE, exist_ok=True)

# --------------------------
# Step 1: Upload + Extract PDF
# --------------------------
@app.post(UPLOAD_ROUTE)
async def upload_pdf(x: int, y: int, file: UploadFile = File(...)):
    uid = str(uuid.uuid4())

    async with httpx.AsyncClient() as client:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        endpoint1_url = ENDPOINT_1.format(x=x, y=y)
        response1 = await client.post(endpoint1_url, files=files)

    if response1.status_code != 200:
        return JSONResponse({"error": "Failed to extract PDF data"}, status_code=500)

    extracted_json = response1.json()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response2 = await client.post(ENDPOINT_2, json=extracted_json)

    if response2.status_code != 200:
        return JSONResponse({"error": "Failed to process JSON"}, status_code=500)

    final_json = response2.json()

    json_path = f"{JSON_STORAGE}/{uid}.json"
    async with aiofiles.open(json_path, "w") as f:
        await f.write(json.dumps(final_json, indent=2))

    return {
        "uid": uid,
        "json_file_path": json_path
    }

# --------------------------
# Step 2: Generate (forward to endpoint 3)
# --------------------------
@app.post(GENERATE_ROUTE)
async def generate(request: Request):
    body = await request.json()
    uid = body.get("uid")

    if not uid:
        raise HTTPException(status_code=400, detail="uid is required")

    file_path = f"{JSON_STORAGE}/{uid}.json"

    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {
                "file": (f"{uid}.json", f, "application/json")
            }
            data = {"uid": uid}  # <- sending uid as JSON/field too
            response = await client.post(ENDPOINT_3, data=data, files=files)

    if response.status_code != 200:
        return JSONResponse({"error": "Failed at endpoint 3"}, status_code=500)

    return JSONResponse({
        "message": "Forwarded successfully",
        "response": response.json()
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
