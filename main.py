import json
from typing import Union, Optional

from tkinter import Tk, StringVar, OptionMenu, Button, Label

from cloner import get_audio, VoiceClone, CloneConversation

voices_data = json.loads(open("voices.json").read())["voices"]
voices = [VoiceClone(voice_data) for voice_data in voices_data]

root = Tk()
Label(root, text="Talk to a celebrity!").pack()

clicked = StringVar()
options = [voice.name for voice in voices]
clicked.set(options[0])
voices_select_dropdown = OptionMenu(root, clicked, *options)
voices_select_dropdown.pack()

conversation: Optional[CloneConversation] = None

def start_conversation():
    voices_select_dropdown.pack_forget()
    voice = voices[options.index(clicked.get())]
    conversation = CloneConversation(voice)

    num_inputs = 0

    # while num_inputs < 6:
    #     user_message = get_audio()
    #     conversation.play_response_to_new_message(user_message)
    #     num_inputs += 1

button = Button(root, text="Start talking!", command=start_conversation).pack()

def end_conversation():
    ...


# Execute tkinter
root.mainloop()
