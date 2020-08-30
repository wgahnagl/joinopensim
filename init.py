from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import os.path
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import config
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sites/opensim.sqlite3'

db = SQLAlchemy(app)
class Grids(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    url = db.Column(db.String(400))
    address = db.Column(db.String(400))
    language = db.Column(db.String(50))
    maturity = db.Column(db.String(50))
    grid_type = db.Column(db.String(50))
    focus = db.Column(db.String(100))
    rental = db.Column(db.String(50))
    dmca_info = db.Column(db.String(600))
    more_info = db.Column(db.String(600))
    regions = db.Column(db.Integer)
    users = db.Column(db.Integer) 
    active_users = db.Column(db.Integer)
    def __init__(self, name, url, address, language, maturity, grid_type, focus, rental, dmca_info, more_info, regions, users, active_users):
        self.name = name
        self.url = url
        self.address = address
        self.language = language
        self.maturity = maturity
        self.grid_type = grid_type
        self.focus = focus
        self.rental = rental
        self.dmca_info = dmca_info
        self.more_info = more_info
        self.regions = regions
        self.users = users
        self.active_users = active_users


def getSiteData(): 
    if not os.path.isdir('sites'):
        os.mkdir('sites')
    db.create_all()

    print("getting wiki data")
    getWikiData("Main_Page")
    
    print("getting grid data")
    getGridData()

def getWikiData(page):
    if not os.path.isdir('sites/wiki'):
        os.mkdir('sites/wiki')

    if not os.path.isfile('sites/wiki/' + page):
        pageUrl = 'http://opensimulator.org/wiki/' + page
        pageRequest = requests.get(pageUrl)
        f = open('sites/wiki/' + page, 'wb')
        f.write(pageRequest.content)
        f.close()

def getGridData(): 
    if not os.path.isdir('sites/hgbusiness'):
        os.mkdir('sites/hgbusiness')

    if not os.path.isfile('sites/hgbusiness/grids'):
        pageUrl = 'https://www.hypergridbusiness.com/statistics/opensim-grid-list/'
        pageRequest = requests.get(pageUrl)
        f = open('sites/hgbusiness/grids','wb')
        f.write(pageRequest.content)
        f.close()

    if not os.path.isfile('sites/hgbusiness/gridinfo'):
        pageUrl = 'https://www.hypergridbusiness.com/statistics/opensim-grid-info/'
        pageRequest = requests.get(pageUrl)
        f = open('sites/hgbusiness/gridinfo', 'wb')
        f.write(pageRequest.content)
        f.close() 

    if not os.path.isfile('sites/hgbusiness/gridaddress'):
        pageUrl = 'https://www.hypergridbusiness.com/statistics/active-grids/'
        pageRequest = requests.get(pageUrl)
        f = open('sites/hgbusiness/gridaddress', 'wb')
        f.write(pageRequest.content)
        f.close() 
    

    if not os.path.isfile('sites/hgbusiness/gridstats'):
        cfg = config.Config('config.cfg')
        pageUrl = 'https://www.hypergridbusiness.com/statistics/'+ cfg['month']+'-'+ str(datetime.now().year) + '-opensim-grid-stats/'
        pageRequest = requests.get(pageUrl)
        f = open('sites/hgbusiness/gridstats', 'wb')
        f.write(pageRequest.content)
        f.close() 

    grids = open("sites/hgbusiness/grids")
    gridInfo = open("sites/hgbusiness/gridinfo")
    gridAddress = open("sites/hgbusiness/gridaddress")
    gridStats = open("sites/hgbusiness/gridstats")    
    
    gridsData = grids.read()
    gridInfoData = gridInfo.read()
    gridAddressData = gridAddress.read()
    gridStatsData = gridStats.read()
    
    gridSoup = BeautifulSoup(gridsData, 'html.parser')
    gridInfoSoup = BeautifulSoup(gridInfoData, 'html.parser')
    gridAddressSoup = BeautifulSoup(gridAddressData, 'html.parser')
    gridStatsSoup = BeautifulSoup(gridStatsData, 'html.parser')

    table = gridSoup.find("table", { "id" : "table-ruled" })
    for row in table.findAll("tr"):
        cells = row.findAll("td")    
        if len(cells) == 6:
            if Grids.query.filter_by(name=cells[0].find(text=True)).first() != None:
               continue

            for a in cells[0].find_all('a', href=True):
                gridUrl = a['href']
 
            grid = Grids( 
                    name = cells[0].find(text=True),
                    url = gridUrl,
                    address = "",
                    language = cells[5].find(text=True),
                    maturity = cells[1].find(text=True),
                    grid_type = cells[2].find(text=True),
                    focus = cells[3].find(text=True),
                    rental = cells[4].find(text=True),
                    dmca_info = "",
                    more_info = "",
                    regions = 0,
                    users = 0,
                    active_users = 0,
                    )
            db.session.add(grid)
            db.session.commit()

    table = gridInfoSoup.find("table", { "id" : "table-ruled" })
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            dmca_info = str(cells[1]).strip("<td>").strip("</td>")
            more_info = cells[2].find(text=True)
            grid = Grids.query.filter_by(name=cells[0].find(text=True)).first()
            grid.dmca_info = dmca_info
            grid.more_info = more_info
            db.session.commit()
        
    table = gridAddressSoup.find("table", { "id" : "table-ruled" })
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            grid = Grids.query.filter_by(name=cells[0].find(text=True)).first()
            grid.address = cells[1].find(text=True)
            db.session.commit()

    table = gridStatsSoup.find("table", { "id" : "table-ruled" })
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 7: 
            grid = Grids.query.filter_by(name=cells[0].find(text=True)).first() 
            grid.regions = cells[1].find(text=True)
            grid.users = cells[3].find(text=True)
            grid.active_users = cells[5].find(text=True)
        
    grids.close()
    gridInfo.close()
    gridAddress.close()
    gridStats.close()

sched = BackgroundScheduler(daemon=True)
sched.add_job(getSiteData,'interval',minutes=1440)
sched.start()

def before_request(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs): 
        if not os.path.isdir('sites'):
            getSiteData()

        info = {
                "usersOnline": 100000,
                }

        kwargs["info"] = info
        return func(*args, **kwargs)
    return wrapped_function

@app.route('/')
@before_request
def render_main(info=None):
    return render_template('main.html', info=info)

@app.route('/start')
@before_request
def render_start(info=None):
    return render_template('start.html', info=info)

if __name__ == '__main__':
    app.run('0.0.0.0', 8085)

