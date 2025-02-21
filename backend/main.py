import os
import time
import base64
import datetime
import requests
import jwt
from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

###############################
#   ENV VARIABLES & SETTINGS  #
###############################
# Meshy API key (for 3D conversion)
MESHY_API_KEY = os.getenv("MESHY_API_KEY")
if not MESHY_API_KEY:
    raise Exception("MESHY_API_KEY environment variable is required.")

# Secret key for JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_DEMO_KEY")

# Directory to save 3D models
SAVE_DIR = "/app/models"  # adjust as needed
os.makedirs(SAVE_DIR, exist_ok=True)

###############################
#   FASTAPI INITIALIZATION    #
###############################
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup for Meshy
MESHY_HEADERS = {"Authorization": f"Bearer {MESHY_API_KEY}", "Content-Type": "application/json"}

###############################
#   FAKE "DATABASE" STORAGE   #
###############################
# In-memory user database: {username: {"password": str, "user_id": int}}
users_db = {}
# In-memory models DB: key=user_id => value=list of model file paths
models_db = {}

def get_next_user_id() -> int:
    """Generate the next user ID based on current length of users_db."""
    return len(users_db) + 1

###############################
#   JWT UTILS & AUTH SCHEME   #
###############################
auth_scheme = HTTPBearer()

def create_access_token(user_id: int, expires_in_hours: int = 1) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_access_token(token: str) -> Optional[int]:
    """Return user_id if token is valid, else None."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    """
    FastAPI dependency that extracts the user_id from the Bearer token.
    Raises HTTP 401 if token is invalid or missing.
    """
    token = credentials.credentials  # Extract token string
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user_id

###############################
#   AUTHENTICATION ENDPOINTS  #
###############################
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    """
    Register a new user. In production, you would:
     - Check if username is unique in your real DB
     - Hash the password with bcrypt
     - Store user record securely
    """
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_id = get_next_user_id()
    users_db[username] = {"password": password, "user_id": new_id}
    return {"message": "User registered successfully", "user_id": new_id}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """
    Validate user credentials, then return a JWT.
    """
    user_record = users_db.get(username)
    if not user_record or user_record["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user_record["user_id"])
    return {"token": token}

###############################
#      3D UPLOAD ENDPOINT     #
###############################
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id)  # Protect with JWT
):
    """
    Upload an image, convert it to 3D via Meshy, then download & save GLB locally.
    In production, you'd:
     - Actually store the file in a DB or S3
     - Possibly store the final model in a real DB
    """
    # Read the uploaded image and convert to Data URI
    file_bytes = await file.read()
    image_data_uri = image_to_data_uri(file_bytes)

    # Prepare request payload for Meshy
    payload = {
        "image_url": image_data_uri,
        "enable_pbr": False,
        "should_remesh": True,
        "should_texture": True
    }

    # Make request to Meshy
    try:
        response = requests.post("https://api.meshy.ai/openapi/v1/image-to-3d",
                                 json=payload, headers=MESHY_HEADERS)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("result")
        if not task_id:
            raise HTTPException(status_code=500, detail="Meshy API did not return a task ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meshy API call failed: {str(e)}")

    # Poll for task completion
    while True:
        time.sleep(30)
        task_response = requests.get(f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
                                     headers=MESHY_HEADERS)
        task_json = task_response.json()
        status_ = task_json.get("status")
        if status_ == "SUCCEEDED":
            # Get the final model URL
            model_urls = task_json.get("model_urls", {})
            glb_url = model_urls.get("glb")
            if not glb_url:
                raise HTTPException(status_code=500, detail="No GLB URL found in Meshy response")

            # Build a local filename to save the GLB file
            base_filename = os.path.splitext(file.filename)[0]
            output_filename = os.path.join(SAVE_DIR, f"{base_filename}_{int(time.time())}.glb")

            # Download the GLB file
            try:
                glb_response = requests.get(glb_url, stream=True)
                glb_response.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in glb_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to download GLB: {str(e)}")

            # Save the model path in our "models_db"
            if current_user_id not in models_db:
                models_db[current_user_id] = []
            models_db[current_user_id].append(output_filename)

            return {"model_file": output_filename}

        elif status_ in ["FAILED", "CANCELED"]:
            raise HTTPException(status_code=500, detail=f"Meshy task {status_}")

        # else, keep waiting if still in progress

###############################
#    LIST USER'S 3D MODELS    #
###############################
@app.get("/my-models")
def get_my_models(current_user_id: int = Depends(get_current_user_id)):
    """
    Return a list of model files belonging to the logged-in user.
    """
    return {
        "user_id": current_user_id,
        "models": models_db.get(current_user_id, [])
    }

###############################
#   UTILITY FUNCTIONS         #
###############################
def image_to_data_uri(image_bytes: bytes) -> str:
    """
    Convert image bytes to a Base64 Data URI (JPEG).
    """
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"

@app.get("/")
def home():
    """
    Basic route to confirm the API is running.
    """
    return {"message": "FastAPI with Auth + Meshy 3D Integration running!"}

# If you want to run locally:
#   uvicorn main:app --host 0.0.0.0 --port 8080
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    """
    Register a new player. In production, you'd:
     - Check if username is unique in a real database
     - Hash the password (bcrypt)
     - Store user details securely
    """
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_id = get_next_user_id()
    users_db[username] = {"password": password, "user_id": new_id}
    return {"message": "User registered successfully", "user_id": new_id}