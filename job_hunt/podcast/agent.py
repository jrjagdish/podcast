# podcast/ai_groq.py
import os
from groq import Groq
from django.conf import settings

# load API key from env / settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", getattr(settings, "GROQ_API_KEY", None))
client = Groq(api_key=GROQ_API_KEY)


def generate_podcast_script(topic: str, user_interest: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "You are a professional podcast script writer. "
            "Write a 2-5 minute spoken podcast script with a hook, three practical tips, "
            "a short story/example, and a closing call-to-action. Keep language simple and conversational."
        ),
    }

    user_msg = {
        "role": "user",
        "content": f"Topic: {topic}\nUser interest: {user_interest}\nGenerate the final script only.",
    }

    # choose a Groq model; adjust model name as needed (llama3-70b-8192 or llama3-33b etc)
    model_name = "llama3-70b-8192"

    completion = client.chat.completions.create(
        messages=[system_msg, user_msg],
        model=model_name,
        max_tokens=800,
        temperature=0.7,
    )

    # content lives at completion.choices[0].message.content
    script = completion.choices[0].message.content
    return script
