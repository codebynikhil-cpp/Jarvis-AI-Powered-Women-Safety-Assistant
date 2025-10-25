import asyncio
import aiohttp
from random import randint
from PIL import Image
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables
load_dotenv()
HF_API_KEY = os.getenv('HuggingFaceAPIKey')

# Update the model URL to a working endpoint
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

async def query(payload):
    """Send request to Hugging Face API with timeout and retry"""
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            try:
                async with session.post(API_URL, headers=headers, json=payload, timeout=60) as response:
                    if response.status == 503:
                        print("Model is loading, please wait...")
                        await asyncio.sleep(20)
                        continue
                    elif response.status == 404:
                        print("Error: Model not found. Please check the model URL.")
                        return None
                    response.raise_for_status()
                    return await response.read()
            except aiohttp.ClientError as e:
                print(f"Network error on attempt {attempt + 1}: {e}")
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
            
            if attempt < 2:  # Don't sleep on last attempt
                await asyncio.sleep(5)
    return None

async def generate_single_image(prompt: str, index: int):
    """Generate a single image with optimized parameters"""
    payload = {
        "inputs": f"{prompt}, high quality, detailed, 4k",
        "parameters": {
            "guidance_scale": 7.5,
            "num_inference_steps": 25,
            "seed": randint(0, 1000000)
        }
    }
    
    image_bytes = await query(payload)
    if image_bytes:
        filename = os.path.join("Data", f"{prompt.replace(' ', '_')}{index + 1}.jpg")
        os.makedirs("Data", exist_ok=True)
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return True
    return False

async def generate_images(prompt: str):
    """Generate images concurrently"""
    os.makedirs("Data", exist_ok=True)
    
    tasks = [generate_single_image(prompt, i) for i in range(4)]
    results = await asyncio.gather(*tasks)
    return any(results)  # Return True if at least one image was generated

def GenerateImages(prompt: str):
    """Main function to generate and display images"""
    try:
        if not HF_API_KEY:
            print("Error: HuggingFace API key not found!")
            return False
            
        print(f"Generating images for: {prompt}")
        success = asyncio.run(generate_images(prompt))
        
        if success:
            open_images(prompt)
            return True
        return False
    except Exception as e:
        print(f"Error in image generation: {e}")
        return False

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Unable to open {image_path}")

# Main execution loop
def main():
    """Main loop to monitor ImageGeneration.data file for new requests"""
    data_file = r"Frontend\Files\ImageGeneration.data"
    
    while True:
        try:
            # Read the data file
            with open(data_file, "r") as f:
                data = f.read().strip()
            
            if not data:
                sleep(1)
                continue
            
            # Parse prompt and status
            try:
                prompt, status = data.split(",")
            except ValueError:
                print("Invalid data format in ImageGeneration.data")
                sleep(1)
                continue
            
            # Check if generation is requested
            if status.lower() == "true":
                print(f"Starting image generation for: {prompt}")
                success = GenerateImages(prompt=prompt)
                
                # Reset the status after generation
                with open(data_file, "w") as f:
                    f.write(f"{prompt},False")
                
                if success:
                    print("Images generated successfully!")
                else:
                    print("Failed to generate images")
            
            sleep(1)
            
        except FileNotFoundError:
            print(f"Waiting for {data_file}")
            sleep(1)
        except Exception as e:
            print(f"Error in main loop: {e}")
            sleep(1)

if __name__ == "__main__":
    main()  # Run the monitoring loop