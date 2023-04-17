import os
import json
from enum import Enum
from typing import List
import argparse
import shutil
import requests
import openai
from dotenv import load_dotenv
import time
import speech_recognition as sr

import pyaudio
import wave

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

CHUNK_SIZE = 1024


class VoiceClone:
    # Maps 1:1 onto the JSON data
    name: str
    chatgpt_starter_prompt: str
    elevenlabs_voice_id: str
    elevenlabs_stability: int
    elevenlabs_similarity_boost: int

    def __init__(self, json_data):
        self.name = json_data["person-name"]
        self.chatgpt_starter_prompt = json_data["chatgpt-starter-prompt"]
        self.elevenlabs_voice_id = json_data["elevenlabs-voice-id"]
        self.elevenlabs_stability = json_data["elevenlabs-stability"]
        self.elevenlabs_similarity_boost = json_data["elevenlabs-similarity-boost"]

    def __repr__(self):
        return f"InteractiveVoice(id={self.id}, name={self.name}, chatgpt_starter_prompt={self.chatgpt_starter_prompt}, elevenlabs_voice_id={self.elevenlabs_voice_id})"

    @property
    def elevenlabs_settings(self):
        return {
            "stability": self.elevenlabs_stability,
            "similarity_boost": self.elevenlabs_similarity_boost,
        }


class ChatGPTConversationMessageRole(Enum):
    # Just to make sure we don't accidentally pass an invalid string
    system = "system"
    user = "user"
    assistant = "assistant"


class ChatGPTConversationMessage:
    # To easily represent and manipulate the messages property, and avoid missing dictionary keys
    role: ChatGPTConversationMessageRole
    content: str

    def __init__(self, role, content):
        self.role = role
        self.content = content


class CloneConversation:
    # Wrapper class for an entire conversation. Initiate it for each new user session.

    voice: VoiceClone
    message_objects: List[ChatGPTConversationMessage] = []

    status_message: str = "Say something!"

    @property
    def messages(self):
        return [
            {"role": message.role.value, "content": message.content}
            for message in self.message_objects
        ]

    def __init__(self, voice: VoiceClone):
        self.voice = voice
        initial_system_message = ChatGPTConversationMessage(
            ChatGPTConversationMessageRole.system, voice.chatgpt_starter_prompt
        )
        self.message_objects.append(initial_system_message)

    def record(self):
        self.status_message = "Recording for 5 seconds..."
        # Set up audio stream
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )

        # Record audio
        frames = []
        for i in range(0, int(44100 / 1024 * 5)):  # Record for 8 seconds
            data = stream.read(1024)
            frames.append(data)

        # Stop audio stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save audio to file
        waveFile = wave.open("audio.wav", "wb")
        waveFile.setnchannels(1)
        waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(44100)
        waveFile.writeframes(b"".join(frames))
        waveFile.close()
        self.status_message = "Finished recording"
        return

    def transcribe(self):
        r = sr.Recognizer()
        with sr.AudioFile("audio.wav") as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            print(text)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return ""

    def get_audio(self) -> str:
        self.record()
        return self.transcribe()

    # Private method
    def __get_agent_chat_completion(self, new_user_message: str) -> str:
        self.status_message = "Getting response from ChatGPT..."
        new_message = ChatGPTConversationMessage(
            ChatGPTConversationMessageRole.user, new_user_message
        )
        self.message_objects.append(new_message)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
        )
        """
        Sample response:
        {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "\n\nHello there, how may I assist you today?",
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21
            }
        }
        """
        response_message = response.choices[0]["message"]["content"]
        new_agent_message = ChatGPTConversationMessage(
            ChatGPTConversationMessageRole.assistant, response_message
        )
        self.message_objects.append(new_agent_message)
        print(f"{response_message=}")
        return response_message

    # Private method

    def __play_tts_stream(self, agent_text: str):
        self.status_message = "Synthesising audio..."
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice.elevenlabs_voice_id}"
        body = {"text": agent_text, "voice_settings": self.voice.elevenlabs_settings}
        headers = {
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": ELEVENLABS_API_KEY,
        }
        response = requests.post(url, json=body, headers=headers, stream=True)
        print(response.raw)
        with open("sample.wav", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        
        self.status_message = "Playing audio..."
        os.system("ffplay sample.wav -nodisp -autoexit")

    # Public method
    def play_response_to_new_message(self, user_message: str) -> str:
        if len(self.message_objects) > 20:
            raise Exception("Too many messages in conversation, terminating")

        agent_text = self.__get_agent_chat_completion(user_message)
        self.__play_tts_stream(agent_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    args, remaining = parser.parse_known_args()
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser],
    )
    parser.add_argument(
        "-v",
        "--voice",
        type=int,
    )
    args = parser.parse_args(remaining)
    voice_json_data = json.loads(open("voices.json").read())["voices"]
    selected_voice = VoiceClone(voice_json_data[args.voice])
    conversation = CloneConversation(selected_voice)

    num_inputs = 0

    while num_inputs < 20:
        user_message = conversation.get_audio()
        conversation.play_response_to_new_message(user_message)
        num_inputs += 1
