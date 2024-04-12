from flask import Flask, request
from flask_cors import cross_origin, CORS
from main import get_token, auth, get_message_history
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import json
import time

app = Flask(__name__)
response = get_token(auth)
lock = asyncio.Lock()
cors = CORS(app, resources={r"*": {"origins": "*"}})

if response != 1:
    giga_token = response.json()['access_token']
    expires_at = response.json()['expires_at']


@app.route('/api/send-message', methods=['POST', 'GET'])
async def give_greeting():
    if round(time.time()*1000) >= expires_at:
        async with lock:
            refresh()
    request_data = request.form  # Получаем JSON из тела запроса
    history = json.loads(request_data.get('history'))
    if history is None or len(history) == 0:
        conversation_history = None
    else:
        conversation_history = history
    response, conversation_history = await get_message_history(giga_token, conversation_history)
    response_data = response.json()
    return json.dumps(response_data['choices'][0]['message'])


def refresh():
    global giga_token, expires_at
    response = get_token(auth)
    if response != 1:
        giga_token = response.json()['access_token']
        expires_at = response.json()['expires_at']
    return


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567)