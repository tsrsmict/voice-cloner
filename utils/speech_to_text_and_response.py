#parse audio input and use gpt to generate response
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def speech_to_text(audio):
    return openai.Audio.transcribe("whisper-1", audio)    
def gpt_response(prompts,person):
    message = [{"role":"system","content":"You are "+person}]+prompts
    response = openai.ChatCompletion.create(
    model=  "gpt-3.5-turbo",
    messages=message,
    )
    prompts.append({ "role": "assistant", "content": response.choices[0]["message"]["content"]});
    return prompts