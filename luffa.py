import json
import re
import traceback
from bottle import default_app, get, post, request, HTTPError
from urllib.request import Request, urlopen
from utils import get_channel, get_settings, get_user, translate_user

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
    text = data.get('text')
    username = data.get('user_name')
    avatar = get_user(team, data.get('user_id'))['profile']['image_192'],

    for site, info in settings.items():
        if site == team:
            continue    # Skip ourselves

        def replace_id(match):
            if match.group(1) == '#':
                return '#{}'.format(get_channel(team, match.group(2)))
            else:
                return translate_user(team, site, match.group(2))

        text_translated = re.sub(r'<([@#])([^\|>]+)(\|[^>]+)?>', replace_id, text)
        message = {
            "username": username,
            "icon_url": avatar,
            "text": text_translated,
        }

        query = Request(info['publish_hook'], data=json.dumps(message, ensure_ascii=False).encode('utf-8'))
        query.add_header('Content-Type', 'application/json')

        try:
            urlopen(query)
        except:
            traceback.print_exc()
            return HTTPError(status=502)

    return ''

application = default_app()
