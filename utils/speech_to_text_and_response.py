#parse audio input and use gpt to generate response
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def speech_to_text(audio):
    return openai.Audio.transcribe("whisper-1", audio)    
    