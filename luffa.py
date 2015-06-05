import json
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
    if team not in settings or request.forms.get('token') != settings[team]['token']:
        return HTTPError(status=401)

    # Skip bot messages
    if request.forms.get('user_name') == 'slackbot':
        return ''

    # Build up message payload
    message = {
        "username": "{} ({})".format(request.forms.get('user_name'), settings[team]['slug']),
        "text": request.forms.get('text'),
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
