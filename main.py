import json
from typing import Optional

from flask import Flask, render_template,request
from flask import jsonify



from cloner import VoiceClone, CloneConversation


voices_data = json.loads(open("voices.json").read())["voices"]
voices = [VoiceClone(voice_data) for voice_data in voices_data]

conversation: Optional[CloneConversation] = None

def start_conversation(voice: VoiceClone = voices[0]):
    global conversation
    conversation = CloneConversation(voice)

    num_inputs = 0
    while num_inputs < 20 and conversation is not None:
        user_message = conversation.get_audio()
        if conversation is not None:
            conversation.play_response_to_new_message(user_message)
        num_inputs += 1

app = Flask(__name__)

@app.route("/")
def index():
    voices = json.loads(open("voices.json").read())["voices"]
    return render_template("index.html", voices=voices)

@app.route("/start-conversation")
def start_conversation_route():
    args = request.args
    voice_id = int(args.get("voice"))
    voice = voices[voice_id]
    start_conversation(voice=voice)
    return "Started conversation"

@app.route("/conversation-status")
def conversation_status():
    global conversation
    if conversation is None:
        return "No conversation"
    return jsonify(status=conversation.status_message)

@app.route("/end-current-conversation")
def end_current_conversation():
    global conversation
    conversation = None
    print("Ended conversation")
    return "Ended conversation"

if __name__=="__main__":
    app.run(debug=False, port=5001,threaded=True)

