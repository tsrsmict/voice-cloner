#parse audio input and use gpt to generate response
import openai
from dotenv import load_dotenv
import os
import speech_recognition as sr
import time

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

conversation=[]
# def speech_to_text(audio):
#     return openai.Audio.transcribe("whisper-1", audio)    
def gpt_response(prompts,person):
    message = [{"role":"system","content":"You are "+person}]+prompts
    response = openai.ChatCompletion.create(
    model=  "gpt-3.5-turbo",
    messages=message,
    )
    print(response.choices[0]["message"]["content"])
    prompts.append({ "role": "assistant", "content": response.choices[0]["message"]["content"]});
    return prompts
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        # r.adjust_for_ambient_noise(source)
        r.energy_threshold=200
        print("Say something!")
        audio = r.listen(source)
        print("Got it! Now to recognize it...")
    said = ""
    try:
        said = r.recognize_whisper_api(audio)
    except Exception as e:
        print("Exception: " + str(e))
    return said


async def converse():
    n=0
    while(n!=6):
        text =await get_audio()
        conversation.append({ "role": "user", "content": text})
        await gpt_response(conversation,"David Attenborough")
        n+=1
converse()