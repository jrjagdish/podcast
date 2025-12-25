# podcast/cloudinary_upload.py
import cloudinary
import cloudinary.uploader
from io import BytesIO
from uuid import uuid4
import os
from django.conf import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_audio_to_cloudinary(audio_bytes: bytes, public_id_prefix: str = "tts") -> str:
    """
    Upload audio bytes directly to Cloudinary.
    
    Args:
        audio_bytes: Audio file bytes
        public_id_prefix: Prefix for the public ID
    
    Returns:
        Cloudinary secure URL
    """
    upload_result = cloudinary.uploader.upload(
        file=BytesIO(audio_bytes),
        resource_type="video",  # Use "video" for audio files
        folder="podcast_audio/",
        public_id=f"{public_id_prefix}_{uuid4().hex}",
        overwrite=True,
        format="wav"
    )
    
    return upload_result["secure_url"]