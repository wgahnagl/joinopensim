from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import os.path
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opensim.sqlite3'


db = SQLAlchemy(app)
class grids(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   url = db.Column(db.String(400))
   address = db.Column(db.String(400))
   language = db.Column(db.String(50))
   maturity = db.Column(db.String(50))
   grid_type = db.Column(db.String(50))
   focus = db.Column(db.String(100))
   rental = db.Column(db.String(50))
   more_info = db.Column(db.String(600))

def __init__(self, url, address, language, maturity, grid_type, focus, rental, more_info):
   self.url = url
   self.address = address
   self.language = language
   self.maturity = maturity
   self.grid_type = grid_type
   self.focus = focus
   self.rental = rental
   self.more_info = more_info


def handleMissingWikiData(page):
    if not os.path.isdir('wiki'):
        os.mkdir('wiki')

    if not os.path.isfile('wiki/' + page):
        pageUrl = 'http://opensimulator.org/wiki/' + page
        pageRequest = requests.get(pageUrl)
        open('wiki/' + page, 'wb').write(pageRequest.content).close()

def generateSimList():
    if not os.path.isdir('hgbusiness'):
        os.mkdir('hgbusiness')

    if not os.path.isfile('hgbusiness/grids'):
        pageUrl = 'https://www.hypergridbusiness.com/statistics/opensim-grid-list/'
        pageRequest = requests.get(pageUrl)
        open('hgbusiness/grids', 'wb').write(pageRequest.content).close()

    if not os.path.isfile('hgbusiness/gridinfo'):
        pageUrl = 'https://www.hypergridbusiness.com/statistics/opensim-grid-info/'
        pageRequest = requests.get(pageUrl)
        open('hgbusiness/gridinfo', 'wb').write(pageRequest.content).close()

    with open('hgbusiness/grids', 'r') as f :
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
    
    with open('hgbusiness/gridinfo', 'r') as f :
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
    


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
    handleMissingWikiData("Main_Page")
    return render_template('main.html', info=info)

@app.route('/start')
@before_request
def render_start(info=None):
    generateSimList()
    return render_template('start.html', info=info)



if __name__ == '__main__':
    app.run('0.0.0.0', 8085)

