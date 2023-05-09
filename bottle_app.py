# A very simple Bottle Hello World app for you to get started with...
from bottle import default_app, route, request
import json
import requests

file = open("/home/creep04ek/mysite/conf.json", "r")
CONFIG = json.loads(file.read())
file.close()

API_KEY = CONFIG['api-key']
MODEL = CONFIG['model']
BOT_TOKEN = CONFIG['bot_token']

def openAI(prompt):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model':MODEL, 'messages': [{"role":"user", "content":prompt}], 'temperature': 0.4, 'max_tokens':300}
    );
    result = response.json()
    print(result)
    final_result = ''.join(choice['message']['content'] for choice in result['choices'])
    return final_result

def openAIImage(prompt):
    response = requests.post(
        'https://api.openai.com/v1/images/generations',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'prompt': prompt,'n' : 1, 'size': '1024x1024'}
    );
    response = json.loads(response.text)
    return response['data'][0]['url']

def answerTelegram(payload):
    data = {
            'chat_id': payload['message']['chat']['id'],
            'text': openAIImage(payload['message']['text'].replace("/img", "")) if "/img" in payload['message']['text'] else openAI(payload['message']['text']),
            'reply_to_message_id': payload['message']['message_id']
        }
    requests.post(
    'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
    json=data
    )

@route('/', method='POST')
def hello_world():
    payload = json.load(request.body)
    if payload['message']['chat']['id'] in CONFIG['allowed']:
        answerTelegram(payload)

application = default_app()

