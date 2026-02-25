import streamlit as st
from groq import Groq
import os

# Retrieve API Key from st.secrets (recommended for deployment)
# For local testing, add this to .streamlit/secrets.toml:
# GROQ_API_KEY = "your_key_here"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

def get_groq_client():
    """Initializes and returns the Groq client."""
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)

@st.cache_data(ttl=3600)  # Cache insights for 1 hour
def generate_ai_insight(prompt: str) -> str:
    """Sends a prompt to Groq LLM and returns the generated text."""
    try:
        client = get_groq_client()
        if not client:
            return "A local favorite known for its consistent quality and great atmosphere."
            
        completion = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and efficient model
            messages=[
                {"role": "system", "content": "You are a witty Bangalore food expert. Provide very concise, single-sentence restaurant insights (max 20 words)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        return completion.choices[0].message.content.strip().strip('"')
    except Exception as e:
        # Fallback to a generic insight if API fails
        return "A local favorite known for its consistent quality and great atmosphere."
