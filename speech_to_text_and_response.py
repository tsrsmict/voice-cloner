#parse audio input and use gpt to generate response
import openai
from dotenv import load_dotenv
import os
import speech_recognition as sr
import requests
import json
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

conversation=[]
# def speech_to_text(audio):
#     return openai.Audio.transcribe("whisper-1", audio)    
def gpt_response(prompts,person):
    print("piping gpt response")
    proompt = '''Imagine you are a grade 12 student from New Delhi, India, named'''+person+'''. You study at The Shri Ram School. You are the head of the school's computer club. You are highly interested in computer science but have diverse interests as well. 

You are kind and modest. When prompted, you speak no more than 50 words. You keep the topic of the conversation polite and interesting. When asked to respond to something that an AI language model cannot respond to, but that he can, you provide the response that he is most likely to give without any hesitation. You speak as a 12th-grade student would. When asked about anything to do with your personality, you respond as he would.

I will play the role of another student from the same school. I will ask you short questions and have a short conversation with you. You will respond in 50 words or less each time.
'''
    message = [{"role":"system","content":proompt}]+prompts
    response = openai.ChatCompletion.create(
    model=  "gpt-3.5-turbo",
    messages=message,
    )
    print(response.choices[0]["message"]["content"])
    prompts.append({ "role": "assistant", "content": response.choices[0]["message"]["content"]});
    return [prompts,response.choices[0]["message"]["content"]]
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
        said = r.recognize_google(audio)
        print(said)
    except Exception as e:
        print("Exception: " + str(e))
    return said

def converse():
    n=0
    while(n!=6):
        text = get_audio()
        conversation.append({ "role": "user", "content": text})
        gpt = gpt_response(conversation,"Arjun Sharma")
        response_text = gpt[1]

        # FIX PLSS
        # req = requests.post("https://api.elevenlabs.io/v1/text-to-speech/nl7Mwvj3wnrdOsUvZX5Y",
        #                    data={"text":respose_text,
        #                          "voice_settings":{
        #                               "stability":0.5,
        #                               "similarity_boost":0,
        #                          }
        #                         },
        #                     headers={"Content-Type":"application/json",
        #                              "xi-api-key":"08ecc14a31f4ebef7499ad7fd038794a",
        #                              'accept':"*/*"})
        # print(req.text)

        n+=1
converse()