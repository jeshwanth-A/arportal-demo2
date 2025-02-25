from fastapi import FastAPI, File, UploadFile, Form
import requests
import os
import base64
import time
from dotenv import load_dotenv  # Load environment variables
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# Load environment variables from .env file
load_dotenv()

# Define FastAPI app
app = FastAPI()

# Load API Key from environment variable
API_KEY = os.getenv("MESHY_API_KEY")
if not API_KEY:
    print("Warning: API Key not found. Please set MESHY_API_KEY environment variable.")
    API_KEY = input("Enter your API key: ")

# Request headers for the Meshy API
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Set the directory where the downloaded 3D model will be saved
SAVE_DIR = "/app/3D_Models"
os.makedirs(SAVE_DIR, exist_ok=True)

# 🔹 **CORS Middleware (Fix for Frontend Access)**
FRONTEND_URL = "https://calmbeat.live"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # ✅ Explicitly allow frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Allow all HTTP methods
    allow_headers=["*"],  # ✅ Allow all headers
)

@app.get("/")
def home():
    return {"message": "Backend is running! Visit /docs for API documentation."}

def image_to_data_uri(image_bytes: bytes) -> str:
    """
    Convert image bytes to a Base64 Data URI.
    """
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), username: str = Form("guest")):
    print(f"📥 Received file: {file.filename}, Type: {file.content_type}, User: {username}")
    try:
        # Read file & convert to Base64 Data URI
        file_bytes = await file.read()
        image_data_uri = image_to_data_uri(file_bytes)

        # Payload for Meshy API
        payload = {
            "image_url": image_data_uri,
            "enable_pbr": False,
            "should_remesh": True,
            "should_texture": True
        }

        response = requests.post("https://api.meshy.ai/openapi/v1/image-to-3d", json=payload, headers=HEADERS)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("result")

        if not task_id:
            return JSONResponse(content={"error": "Task ID not received", "details": task_data}, status_code=500)

        print(f"✅ Task Created: {task_id}")

        # Poll for task completion
        while True:
            time.sleep(30)  # Wait before checking status again
            task_response = requests.get(f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}", headers=HEADERS)
            task_status = task_response.json()
            status = task_status.get("status")
            progress = task_status.get("progress", 0)
            print(f"⏳ Task Status: {status}, Progress: {progress}%")

            if status == "SUCCEEDED":
                # Get GLB file URL
                model_urls = task_status.get("model_urls", {})
                glb_url = model_urls.get("glb")

                if not glb_url:
                    return JSONResponse(content={"error": "3D model URL not found", "details": task_status}, status_code=500)

                print(f"🎉 3D Model Ready: {glb_url}")

                # Save the file locally
                base_filename = os.path.splitext(file.filename)[0]
                output_filename = f"{base_filename}_{int(time.time())}.glb"
                file_path = os.path.join(SAVE_DIR, output_filename)

                print(f"📥 Downloading {glb_url} to {file_path} ...")
                glb_response = requests.get(glb_url, stream=True)
                glb_response.raise_for_status()

                with open(file_path, "wb") as f:
                    for chunk in glb_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"✅ Download complete! File saved at {file_path}")

                # Return correct download URL
                download_url = f"https://backend-service-686596926199.us-central1.run.app/download/{output_filename}"
                return JSONResponse(content={"model_file": output_filename, "download_url": download_url})

            elif status in ["FAILED", "CANCELED"]:
                return JSONResponse(content={"error": f"Task {status}", "details": task_status}, status_code=500)

    except Exception as e:
        print("❌ Error processing file:", str(e))
        return JSONResponse(content={"error": "Internal Server Error", "details": str(e)}, status_code=500)

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(SAVE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
    return JSONResponse(content={"error": "File not found"}, status_code=404)