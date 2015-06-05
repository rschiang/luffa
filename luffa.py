from bottle import route

@route('/')
def index():
    return 'It works!'

@route('/broadcast')
def broadcast():
    return 'All is well'
