import tkinter as tk
from tkinter import messagebox
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageTk
import os

# Placeholder function: Replace this with your actual LoRA integration logic.
def apply_lora_weights(pipeline, lora_path):
    print(f"Applying LoRA weights from {lora_path}")
    # TODO: Add your LoRA application code here.
    return pipeline

class FluxApp:
    def __init__(self, master):
        self.master = master
        master.title("Flux Dev - AI Image Generator with LoRA")
        
        # Prompt entry
        self.prompt_label = tk.Label(master, text="Enter prompt:")
        self.prompt_label.pack(pady=(10, 0))
        self.prompt_entry = tk.Entry(master, width=50)
        self.prompt_entry.pack(pady=(0, 10))
        
        # Define folder paths based on your directory structure:
        # Downloads/imagen5 -> base model folder
        # Downloads/imagen5/lora3 -> folder containing LoRA .safetensors file(s)
        self.downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.model_folder = os.path.join(self.downloads_folder, "imagen5")
        self.lora_folder = os.path.join(self.model_folder, "lora3")
        
        # Get list of LoRA files from the lora3 folder
        self.lora_files = self.get_lora_files()
        
        # Dropdown menu for selecting a LoRA file (if available)
        if self.lora_files:
            self.selected_lora = tk.StringVar(master)
            self.selected_lora.set(self.lora_files[0])
            self.lora_menu = tk.OptionMenu(master, self.selected_lora, *self.lora_files)
            self.lora_menu.pack(pady=(0, 10))
        else:
            self.selected_lora = None
            tk.Label(master, text="No LoRA files found in folder.").pack(pady=(0, 10))
        
        # Button to apply the selected LoRA file
        self.apply_lora_button = tk.Button(master, text="Apply Selected LoRA", command=self.apply_lora)
        self.apply_lora_button.pack(pady=(0, 10))
        
        # Button to generate an image
        self.generate_button = tk.Button(master, text="Generate Image", command=self.generate_image)
        self.generate_button.pack(pady=(0, 10))
        
        # Status label for displaying messages
        self.status_label = tk.Label(master, text="Loading model...", fg="blue")
        self.status_label.pack()
        
        # Label for displaying the generated image
        self.image_label = tk.Label(master)
        self.image_label.pack(pady=(10, 10))
        
        # Load the base model
        self.pipeline = None
        self.load_model()
        
    def get_lora_files(self):
        """List all .safetensors files in the lora3 folder."""
        if os.path.exists(self.lora_folder):
            files = [f for f in os.listdir(self.lora_folder) if f.endswith(".safetensors")]
            return files
        return []
    
    def load_model(self):
        """Load the Flux Dev model from the imagen5 folder."""
        try:
            # Load the base model from the Downloads/imagen5 folder
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_folder,
                torch_dtype=torch.float16,
                revision="fp16"  # Use this if your model uses fp16 weights
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipeline.to(device)
            self.status_label.config(text="Model loaded successfully.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error loading model: {e}", fg="red")
            self.pipeline = None
    
    def apply_lora(self):
        """Apply the selected LoRA file to the model."""
        if not self.selected_lora:
            self.status_label.config(text="No LoRA file selected.", fg="orange")
            return
        lora_file = os.path.join(self.lora_folder, self.selected_lora.get())
        self.status_label.config(text=f"Applying LoRA: {self.selected_lora.get()}...", fg="blue")
        self.master.update()
        self.pipeline = apply_lora_weights(self.pipeline, lora_file)
        self.status_label.config(text=f"LoRA applied: {self.selected_lora.get()}", fg="green")
    
    def generate_image(self):
        """Generate an image using the (possibly modified) model from a given prompt."""
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt.")
            return
        if not self.pipeline:
            messagebox.showerror("Error", "Model not loaded properly.")
            return
        self.status_label.config(text="Generating image...", fg="blue")
        self.master.update()
        try:
            result = self.pipeline(prompt, num_inference_steps=50)
            image = result.images[0]
            image_path = "generated_image.png"
            image.save(image_path)
            
            # Display the generated image in the GUI
            pil_image = Image.open(image_path)
            tk_image = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image  # Keep a reference to avoid garbage collection
            self.status_label.config(text="Image generated successfully.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error generating image: {e}", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = FluxApp(root)
    root.mainloop()