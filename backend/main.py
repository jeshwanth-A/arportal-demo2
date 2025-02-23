import os
import time
import base64
import datetime
import requests
import jwt
from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
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
SAVE_DIR = "models"
os.makedirs(SAVE_DIR, exist_ok=True)

app = FastAPI()

# 🔥 FIX CORS ERROR: Allow frontend requests 🔥
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
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
    print(f"🔍 Admin Panel Access Attempt by: {current_user}")

    # Ensure user exists in database
    if current_user not in users_db:
        print("⛔ User not found in users_db!")
        raise HTTPException(status_code=403, detail="User not found")

    # Check if user is an admin
    if not users_db[current_user].get("is_admin", False):
        print("⛔ Access Denied! User is not an admin.")
        raise HTTPException(status_code=403, detail="Admin access required")

    print("✅ Admin Access Granted. Returning User List.")
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

    while True:
        time.sleep(30)
        task_response = requests.get(f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}", headers=MESHY_HEADERS)
        task_json = task_response.json()
        status_ = task_json.get("status")

        if status_ == "SUCCEEDED":
            model_urls = task_json.get("model_urls", {})
            glb_url = model_urls.get("glb")

            if not glb_url:
                raise HTTPException(status_code=500, detail="No GLB URL found in Meshy response")

            base_filename = os.path.splitext(file.filename)[0]
            output_filename = os.path.join(SAVE_DIR, f"{base_filename}_{int(time.time())}.glb")

            try:
                glb_response = requests.get(glb_url, stream=True)
                glb_response.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in glb_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to download GLB: {str(e)}")

            if current_user not in models_db:
                models_db[current_user] = []
            models_db[current_user].append(output_filename)

            return {"model_file": output_filename}

        elif status_ in ["FAILED", "CANCELED"]:
            raise HTTPException(status_code=500, detail=f"Meshy task {status_}")

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