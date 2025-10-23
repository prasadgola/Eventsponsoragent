"""
Media generation tools for image and video creation
Uses Vertex AI for Imagen - OPTIMIZED VERSION
"""

import os
import json
import base64
from typing import Optional
from io import BytesIO

# Import Vertex AI
try:
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    from PIL import Image
    
    # Initialize Vertex AI
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'event-sponsor-assistant')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    aiplatform.init(project=project_id, location=location)
    VERTEX_AVAILABLE = True
    print(f"✅ Vertex AI initialized: {project_id} in {location}")
except ImportError as e:
    print(f"⚠️ PIL not installed, images won't be compressed: {e}")
    VERTEX_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Vertex AI initialization failed: {e}")
    VERTEX_AVAILABLE = False


async def generate_image(prompt: str, reference_image_data: Optional[str] = None) -> str:
    """
    Generate images using Vertex AI Imagen with compression.
    
    Args:
        prompt: Text description of the desired image
        reference_image_data: Optional base64-encoded reference image (not yet supported)
    
    Returns:
        JSON string with image_data (base64) and text_response
    """
    
    if not VERTEX_AVAILABLE:
        return json.dumps({
            "error": "Vertex AI not available",
            "text_response": "Image generation is not available right now. "
                           "Let me help you with event planning, finding sponsors, or processing payments instead!"
        })
    
    try:
        print(f"🎨 Generating image: {prompt[:50]}...")
        
        # Load the Imagen model
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        
        # Generate image with smaller size
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",  # Square images are smaller
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )
        
        # Check if we got an image
        if not response or not response.images or len(response.images) == 0:
            raise Exception("No image was generated")
        
        # Get the image bytes
        image = response.images[0]
        original_bytes = image._image_bytes
        original_size = len(original_bytes) / 1024
        
        print(f"📦 Original image size: {original_size:.1f} KB")
        
        # Compress the image if it's too large (> 500 KB)
        if original_size > 500:
            try:
                # Open with PIL
                pil_image = Image.open(BytesIO(original_bytes))
                
                # Resize if very large
                max_size = 1024
                if pil_image.width > max_size or pil_image.height > max_size:
                    pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                    print(f"🔧 Resized to: {pil_image.width}x{pil_image.height}")
                
                # Compress to JPEG with quality 85
                output = BytesIO()
                pil_image.convert('RGB').save(output, format='JPEG', quality=85, optimize=True)
                compressed_bytes = output.getvalue()
                compressed_size = len(compressed_bytes) / 1024
                
                print(f"✅ Compressed to: {compressed_size:.1f} KB ({(compressed_size/original_size*100):.0f}% of original)")
                
                # Use compressed version
                image_bytes = compressed_bytes
                
            except Exception as compress_error:
                print(f"⚠️ Compression failed, using original: {compress_error}")
                image_bytes = original_bytes
        else:
            image_bytes = original_bytes
            print(f"✅ Size OK, no compression needed")
        
        # Convert to base64
        image_data = base64.b64encode(image_bytes).decode('utf-8')
        final_size = len(image_bytes) / 1024
        
        print(f"✅ Image ready! Final size: {final_size:.1f} KB, Base64 length: {len(image_data)}")
        
        result = {
            "image_data": image_data,
            "text_response": f"Here's the image I generated for '{prompt}'!"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        
        # Check for common errors
        error_message = str(e).lower()
        
        if "quota" in error_message:
            user_message = "I've reached the image generation quota. Please try again in a few minutes!"
        elif "billing" in error_message:
            user_message = "Image generation requires billing to be enabled. Let me help you with other tasks!"
        elif "permission" in error_message or "403" in error_message:
            user_message = "I don't have permission to generate images right now."
        else:
            user_message = f"I had trouble generating that image. Let me help you with something else!"
        
        return json.dumps({
            "error": str(e),
            "text_response": user_message
        })


async def generate_video(
    prompt: str, 
    reference_image_data: Optional[str] = None, 
    reference_video_data: Optional[str] = None
) -> str:
    """
    Generate videos using Vertex AI Veo (when available).
    
    Args:
        prompt: Text description of the desired video
        reference_image_data: Optional base64-encoded reference image
        reference_video_data: Optional base64-encoded reference video
    
    Returns:
        JSON string with video_url and text_response
    """
    
    # Video generation with Veo is not yet generally available
    return json.dumps({
        "text_response": f"Video generation is coming soon! For now, I can create images, "
                       f"help you find sponsors, manage email campaigns, or process sponsorship payments. "
                       f"What would you like to do?"
    })