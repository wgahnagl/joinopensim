from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import os.path
from functools import wraps

app = Flask(__name__)

mainPage = ""

def handleMissingFiles(page):
    if not os.path.isdir('wiki'):
        os.mkdir('wiki')

    if not os.path.isfile('wiki/' + page):
        pageUrl = 'http://opensimulator.org/wiki/' + page
        pageRequest = requests.get(pageUrl)
        open('wiki/' + page, 'wb').write(pageRequest.content).close()

def before_request(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        info = {
            "usersOnline": 100000,
        }
    
        kwargs["info"] = info
        return func(*args, **kwargs)
    return wrapped_function


@app.route('/')
@before_request
def render_main(info=None):
    handleMissingFiles("Main_Page")
    with open('wiki/Main_Page', 'r') as f : 
        contents = f.read() 
        soup = BeautifulSoup(contents, 'html.parser')
        usersOnline = 10
    return render_template('main.html', info=info)


if __name__ == '__main__':
        app.run('0.0.0.0', 8085)

