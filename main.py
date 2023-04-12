from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from dotenv import load_dotenv
load_dotenv()
from utils import speech_to_text_and_response as  stt
import os

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
    conversation = []
    if request.method == "POST":
        # print(request.form['conversation']) fix this
        # conversation = request.form.get('conversation')
        f = request.files['audio_data']
        f.save(os.path.join('', "audio.wav"))
        with open("audio.wav", 'rb') as audio:
            text  = stt.speech_to_text(audio)['text']
            conversation.append({"role":"user","content":text})
            conversation = stt.gpt_response(conversation,"David Attenborough") #need to refactor to add choices
        print(conversation)
        return render_template('index.html', request="POST", conversation=conversation)
    else:
        return render_template("index.html",conversation=[])


if __name__ == "__main__":
    app.run(debug=True)