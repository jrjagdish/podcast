# podcast/uploaders.py
import os
from supabase import create_client, Client
from django.conf import settings
from uuid import uuid4

SUPABASE_URL = os.getenv("SUPABASE_URL", getattr(settings, "SUPABASE_URL", None))
SUPABASE_KEY = os.getenv("SUPABASE_KEY", getattr(settings, "SUPABASE_KEY", None))
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_path: str) -> str:
    bucket = "podcast-audio"
    filename = f"audio/{uuid4().hex}.mp3"
    with open(file_path, "rb") as f:
        res = supabase.storage.from_(bucket).upload(filename, f)
        # check result
        if res.get("error"):
            raise Exception(res["error"])
    pub = supabase.storage.from_(bucket).get_public_url(filename)
    # pub returns dict structure: {"publicUrl": "..."} depending on client version
    if isinstance(pub, dict):
        return pub.get("publicUrl") or pub.get("public_url") or pub.get("publicURL")
    return pub
