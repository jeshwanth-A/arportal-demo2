from fastapi import FastAPI, Form, File, UploadFile, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import base64
import datetime
import requests
import jwt
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

###############################
#   Environment Variables     #
###############################
MESHY_API_KEY = os.getenv("MESHY_API_KEY")
if not MESHY_API_KEY:
    raise Exception("MESHY_API_KEY environment variable is required.")

SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_DEMO_KEY")

# ✅ Ensure models are saved inside the Downloads folder for easy access
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "3D_Models")
os.makedirs(SAVE_DIR, exist_ok=True)

app = FastAPI()

# ✅ CORS: Allow frontend requests securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],  # Replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

MESHY_HEADERS = {"Authorization": f"Bearer {MESHY_API_KEY}", "Content-Type": "application/json"}
auth_scheme = HTTPBearer()

###############################
#   In-Memory Database       #
###############################
users_db = {}  # { "username": { "password": "password123", "is_admin": False } }
models_db = {}  # { "username": ["model1.glb", "model2.glb"] }
tasks_db = {}  # { "task_id": { "username": "user", "filename": "path/to/file.glb", "status": "PENDING" } }

###############################
#   JWT Utilities & Auth      #
###############################
def create_access_token(username: str, expires_in_hours: int = 24) -> str:
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> Optional[str]:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("username")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    return decode_access_token(credentials.credentials)

###############################
#   Authentication Endpoints  #
###############################
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    users_db[username] = {"password": password, "is_admin": username == "mvsr"}
    
    return {"message": "User registered successfully"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username not in users_db or users_db[username]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    is_admin = users_db[username]["is_admin"]
    token = create_access_token(username)
    
    return {"token": token, "is_admin": is_admin}

@app.get("/all-users")
def get_all_users(current_user: str = Depends(get_current_user)):
    if current_user not in users_db or not users_db[current_user].get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"users": users_db}

###############################
#   Model Upload & Retrieval  #
###############################
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    file_bytes = await file.read()
    image_data_uri = image_to_data_uri(file_bytes)

    payload = {
        "image_url": image_data_uri,
        "enable_pbr": False,
        "should_remesh": True,
        "should_texture": True
    }

    try:
        response = requests.post("https://api.meshy.ai/openapi/v1/image-to-3d", json=payload, headers=MESHY_HEADERS)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("result")

        if not task_id:
            raise HTTPException(status_code=500, detail="Meshy API did not return a task ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meshy API call failed: {str(e)}")

    base_filename = os.path.splitext(file.filename)[0]
    output_filename = os.path.join(SAVE_DIR, f"{base_filename}_{int(time.time())}.glb")
    tasks_db[task_id] = {
        "username": current_user,
        "filename": output_filename,
        "status": "PENDING"
    }

    return {"task_id": task_id}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str, current_user: str = Depends(get_current_user)):
    if task_id not in tasks_db or tasks_db[task_id]["username"] != current_user:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    task_info = tasks_db[task_id]
    return {"status": task_info["status"]}

@app.get("/download/{task_id}")
def download_file(task_id: str, current_user: str = Depends(get_current_user)):
    if task_id not in tasks_db or tasks_db[task_id]["username"] != current_user:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    task_info = tasks_db[task_id]
    if task_info["status"] != "SUCCEEDED":
        raise HTTPException(status_code=400, detail="Task not completed or failed")

    return FileResponse(
        path=task_info["filename"],
        filename=os.path.basename(task_info["filename"]),
        media_type="application/octet-stream"
    )

@app.get("/my-models")
def get_my_models(current_user: str = Depends(get_current_user)):
    return {"models": models_db.get(current_user, [])}

###############################
#   Utility Functions         #
###############################
def image_to_data_uri(image_bytes: bytes) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

@app.get("/")
def home():
    return {"message": "FastAPI with Meshy 3D Integration running!"}

###############################
#   Run FastAPI Locally       #
###############################
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)