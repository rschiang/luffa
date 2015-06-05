import json
import re
import traceback
from bottle import default_app, get, post, request, HTTPError
from urllib.request import Request, urlopen

def get_settings():
    with open('config.json', encoding='utf-8') as f:
        return json.load(f)

@get('/')
def index():
    return 'It works!'

@post('/broadcast/<team>')
def broadcast(team):
    settings = get_settings()
    data = request.forms.decode()
    if team not in settings or data.get('token') != settings[team]['token']:
        return HTTPError(status=401)

    # Skip bot messages
    if data.get('user_name') == 'slackbot':
        return ''

    # Build up message payload
    text = re.sub(r'\<([@#])([^\|]+)\|([^\>]+)\>', r'\1\3', data.get('text'))
    message = {
        "username": "{} ({})".format(data.get('user_name'), settings[team]['slug']),
        "text": text,
    }

    for site, info in settings.items():
        if site == team:
            continue    # Skip ourselves

        query = Request(info['publish_hook'], data=json.dumps(message, ensure_ascii=False).encode('utf-8'))
        query.add_header('Content-Type', 'application/json')

        try:
            urlopen(query)
        except:
            traceback.print_exc()
            return HTTPError(status=502)

    return ''

application = default_app()
