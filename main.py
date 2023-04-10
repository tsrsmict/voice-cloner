from flask import Flask
from flask import request
from flask import render_template
from dotenv import load_dotenv
load_dotenv()
from utils import speech_to_text_and_response as  stt
import os

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        f = request.files['audio_data']
        with open('audio.wav', 'rb') as audio:
            
            print(stt.speech_to_text(audio))
        print('file uploaded successfully')

        return render_template('index.html', request="POST")
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)