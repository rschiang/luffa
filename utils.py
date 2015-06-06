import json
import slacker

def get_settings():
    with open('config.json', encoding='utf-8') as f:
        return json.load(f)

def get_slacker(team):
    settings = get_settings()
    return slacker.Slacker(settings[team]['query_token'])

def get_channel(team, identifier):
    slack = get_slacker(team)
    response = slack.channels.info(identifier).body
    return response['channel']['name'] if response.get('ok') else None

def get_user(team, identifier):
    slack = get_slacker(team)
    response = slack.users.info(identifier).body
    return response['user'] if response.get('ok') else None

def translate_user(team1, team2, identifier):
    user1 = get_user(team1, identifier)
    if user1:
        slack2 = get_slacker(team2)
        users2 = { item['name']: item for item in slack2.users.list().body['members'] }
        user2 = users2.get(user1['name'])
        if user2:
            return '<@{}|{}>'.format(user2['id'], user1['name'])
        else:
            return '@{}'.format(user1['name'])
    else:
        return '@{}'.format(identifier)
