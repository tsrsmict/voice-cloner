from flask import Flask
from dotenv import load_dotenv
load_dotenv()
import os

app  = Flask(__name__)

@app.route('/')
async def index():
    return 'Hello World'

if __name__ == '__main__':
    if(os.getenv('ENV') == 'DEV'):
        app.run(debug=True)