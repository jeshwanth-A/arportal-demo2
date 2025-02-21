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

# Load environment variables from .env file if present
load_dotenv()

###############################
#   Environment Variables     #
###############################
# Meshy API key for 3D model generation (required)
MESHY_API_KEY = os.getenv("MESHY_API_KEY")
if not MESHY_API_KEY:
    raise Exception("MESHY_API_KEY environment variable is required.")

# Secret key for JWT token signing (default is insecure for demo purposes)
SECRET_KEY = os.getenv("SECRET_KEY", "INSECURE_DEMO_KEY")

# Directory to save 3D models
SAVE_DIR = "models"
os.makedirs(SAVE_DIR, exist_ok=True)

###############################
#   FastAPI Initialization    #
###############################
app = FastAPI()

# Add CORS middleware for cross-origin requests (for testing purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Headers for Meshy API requests
MESHY_HEADERS = {"Authorization": f"Bearer {MESHY_API_KEY}", "Content-Type": "application/json"}

###############################
#   In-Memory "Database"      #
###############################
# Stores user data (username, password, user_id) - use a real database in production
users_db = {}

# Stores user models (user_id -> list of model paths)
models_db = {}

def get_next_user_id() -> int:
    """Generate the next user ID."""
    return len(users_db) + 1

###############################
#   JWT Utilities & Auth      #
###############################
auth_scheme = HTTPBearer()

def create_access_token(user_id: int, expires_in_hours: int = 24) -> str:
    """Create a JWT token for the given user ID."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> Optional[int]:
    """Decode and validate a JWT token, returning the user ID."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    """Extract and validate the user ID from the JWT token."""
    token = credentials.credentials
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user_id

###############################
#   Authentication Endpoints  #
###############################
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    """
    Register a new user. Stores in memory (use a database in production).
    """
    print(f"📌 Register attempt: username={username}")

    if username in users_db:
        print("⚠️ Username already exists!")
        raise HTTPException(status_code=400, detail="Username already exists")

    new_id = get_next_user_id()
    users_db[username] = {"password": password, "user_id": new_id}
    print(f"✅ New user registered: {username} (ID {new_id})")

    return {"message": "User registered successfully", "user_id": new_id}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """
    Validate user credentials, then return a JWT.
    """
    if username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_record = users_db[username]
    if user_record["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    token = create_access_token(user_record["user_id"])
    return {"token": token}

###############################
#   Model Management          #
###############################
@app.get("/my-models")
def get_my_models(current_user_id: int = Depends(get_current_user_id)):
    """Return the list of models for the authenticated user."""
    return {
        "user_id": current_user_id,
        "models": models_db.get(current_user_id, [])
    }

@app.get("/all-users")
def get_all_users():
    """
    Fetch all registered users.
    WARNING: This exposes passwords in plain text! Only use for testing.
    """
    return {"users": users_db}

###############################
#   3D Model Upload Endpoint  #
###############################
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Upload an image, convert it to 3D via Meshy API, and save the GLB file locally.
    Requires authentication.
    """
    file_bytes = await file.read()
    image_data_uri = image_to_data_uri(file_bytes)

    payload = {
        "image_url": image_data_uri,
        "enable_pbr": False,
        "should_remesh": True,
        "should_texture": True
    }

    # Submit task to Meshy API
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

    # Poll task status until completion
    while True:
        time.sleep(30)
        task_response = requests.get(f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
                                     headers=MESHY_HEADERS)
        task_json = task_response.json()
        status_ = task_json.get("status")
        if status_ == "SUCCEEDED":
            model_urls = task_json.get("model_urls", {})
            glb_url = model_urls.get("glb")
            if not glb_url:
                raise HTTPException(status_code=500, detail="No GLB URL found in Meshy response")

            base_filename = os.path.splitext(file.filename)[0]
            output_filename = os.path.join(SAVE_DIR, f"{base_filename}_{int(time.time())}.glb")

            # Download and save the GLB file
            try:
                glb_response = requests.get(glb_url, stream=True)
                glb_response.raise_for_status()
                with open(output_filename, "wb") as f:
                    for chunk in glb_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to download GLB: {str(e)}")

            # Store the model path for the user
            if current_user_id not in models_db:
                models_db[current_user_id] = []
            models_db[current_user_id].append(output_filename)

            return {"model_file": output_filename}

        elif status_ in ["FAILED", "CANCELED"]:
            raise HTTPException(status_code=500, detail=f"Meshy task {status_}")

###############################
#   Utility Functions         #
###############################
def image_to_data_uri(image_bytes: bytes) -> str:
    """Convert image bytes to a data URI for Meshy API."""
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"

@app.get("/")
def home():
    """Root endpoint to check if the API is running."""
    return {"message": "FastAPI with Auth + Meshy 3D Integration running!"}

# Run the app locally
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)