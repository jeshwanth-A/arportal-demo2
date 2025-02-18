import requests
import time
import os
import base64

# Load API key from environment variable or prompt user
API_KEY = os.getenv("MESHY_API_KEY")
if not API_KEY:
    print("Warning: API Key not found. Please set MESHY_API_KEY environment variable.")
    API_KEY = input("Enter your API key: ")

# Set the correct image file path
IMAGE_PATH = "flower.jpeg"
if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"Image file '{IMAGE_PATH}' not found.")

# Define custom save directory
#SAVE_DIR = r"C:\Users\your_username\Downloads\3D_Models"  # Windows
SAVE_DIR = "/Users/apple/Downloads/3D_Models"  # Mac/Linux

# Ensure the directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# Function to convert image to base64 Data URI
def image_to_data_uri(image_path):
    with open(image_path, "rb") as image_file:
        base64_data = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"

# Convert image to Data URI
image_data_uri = image_to_data_uri(IMAGE_PATH)

payload = {
    "image_url": image_data_uri,  # Using Data URI
    "enable_pbr": False,
    "should_remesh": True,
    "should_texture": True,
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Create 3D task
response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-3d",
    headers=headers,
    json=payload,
)
try:
    response.raise_for_status()
    task_data = response.json()
    print("API Response:", task_data)  # Debugging output

    # Extract task ID
    TASK_ID = task_data.get("result")  # Updated to match API response
    if not TASK_ID:
        print("Task ID not received. API Response:", task_data)
        exit()
except requests.RequestException as e:
    print(f"Error creating task: {e}, Response: {response.text}")
    exit()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 2: Polling loop
while True:
    response = requests.get(f"https://api.meshy.ai/openapi/v1/image-to-3d/{TASK_ID}", headers=headers)
    task_status = response.json()
    print("Full API Response:", task_status)  # Debugging output

    status = task_status.get("status")
    progress = task_status.get("progress", 0)
    print(f"Task Status: {status}, Progress: {progress}%")

    if status == "SUCCEEDED":
        print("3D Model Ready! Downloading...")

        # Extract .glb model URL
        model_urls = task_status.get("model_urls", {})
        glb_url = model_urls.get("glb")
        
        if glb_url:
            output_filename = os.path.join(SAVE_DIR, "output_model.glb")  # Save to custom folder
            print(f"Downloading {glb_url} to {output_filename} ...")
            
            # Step 3: Download the file
            glb_response = requests.get(glb_url, stream=True)
            glb_response.raise_for_status()  # Ensure no errors

            with open(output_filename, "wb") as file:
                for chunk in glb_response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Download complete! File saved at {output_filename}")
        else:
            print("Error: .glb file URL not found in response.")

        break
    elif status in ["FAILED", "CANCELED"]:
        print(f"Task failed or was canceled: {task_status}")
        break
    
    # Wait before checking again
    time.sleep(10)