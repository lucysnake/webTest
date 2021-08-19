import functools
import sys
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from flaskr.auth import login_required

bp = Blueprint('spiele', __name__)

@bp.route('/shot', methods=('GET','POST'))
@login_required
def test():
        #import database
        db = get_db()

        #test if there is a game
        game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
        if(game is None):
            return(redirect(url_for('index.jo')))

        user_id = session.get('user_id')

        #User submits anzahl
        if request.method == 'POST':
            #get anzahl from HTML
            anz = request.form['anz']
            #get user_id
            #insert into Einsatz                
            gamea = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
            db.execute("INSERT INTO einsatz (spiel_id,anzahlEinsatz,spieler_id) VALUES(?,?,?)",(gamea['id'],anz,user_id))
            db.commit()
            return(redirect(url_for('spiele.gesetzt')))
                    
        #get username
        g.user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        return(render_template('shot.html', username = g.user[1]))


@bp.route('/ges', methods=('GET','POST'))
def gesetzt():
    if request.method == 'POST':
        return(redirect(url_for('spiele.auswerten')))
    user_id = session.get('user_id')
    db = get_db()
    game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
    einsatz = db.execute('SELECT * FROM einsatz WHERE spiel_id = ? AND spieler_id= ?', (game['id'], user_id)).fetchone()
    return render_template('gesetzt.html', anz=einsatz['anzahlEinsatz'])


# Spiel mit game_id auswerten, Einsätze zusammenzählen, Wahrscheinlichkeiten berechenen, Game Attribut run auf 0 setzen
@bp.route('/aus', methods=('GET','POST'))
def auswerten():
    db = get_db()
    game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
    #einsaetze = db.execute('SELECT * FROM einsatz WHERE spiel_id = ?',(game['id'],)).fetchall()
    alleEinsaetze = []
    users = []
    userName = []
    for element in db.execute('SELECT * FROM einsatz WHERE spiel_id = ?',(game['id'],)):
        alleEinsaetze.append(element[2])
        users.append(element[3])
        userName.append(db.execute('SELECT username FROM user WHERE id = ?', (users[-1],)).fetchone()[0])

    '''    
    DEBUG
    print(len(alleEinsaetze), file=sys.stdout)
    print(len(users), file=sys.stdout)
    for i in range(len(alleEinsaetze)):
        print(i,file=sys.stdout)
        print("user: " + str(users[i]) + " hat gesetzt: " + str(alleEinsaetze[i]), file=sys.stdout )
    print("hier", file=sys.stdout)
    '''
    if session.get('user_id') == 1:
        looser_id = random.choices(users,alleEinsaetze)
        looser_name = db.execute('SELECT username FROM user WHERE id = ?', (looser_id[0],)).fetchone()
        print(looser_name[0], file=sys.stdout)
        print(game['id'], file=sys.stdout)
        db.execute("UPDATE game SET looser = ? WHERE id = ?",(looser_name[0], game['id']))
        db.commit()
    else:
        looser_name = db.execute('SELECT looser FROM game WHERE id = ?',(game['id'],)).fetchone()
        if looser_name[0] == None:
            return(redirect(url_for('spiele.gesetzt')))

    #total number of schlücke
    totalS = db.execute('SELECT SUM(anzahlEinsatz) FROM einsatz WHERE spiel_id = ? GROUP BY ?', (game['id'],game['id'])).fetchone()

    #probabilities for every user
    probabilityU = []
    for i in range(len(users)):
        probabilityU.append(
            truncate((db.execute('SELECT anzahlEinsatz FROM einsatz WHERE spiel_id = ? AND spieler_id = ?', (game['id'],users[i])).fetchone()[0]/totalS[0]) * 100, 1)
            )
    
    dic = {
    "brand": 2,
    "model": 3,
    "year": 2
    }
    return render_template('looser.html', looser=looser_name[0], len=len(users), userName=userName, alleEinsaetze=alleEinsaetze, probabilityU=probabilityU, dic=dic)


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


@bp.route('/start', methods=('GET','POST'))
@login_required
def startgame():
    db = get_db()
    db.execute("INSERT INTO game (name,run) VALUES(?,?)",("sauf","1"))
    db.commit()
    return(redirect(url_for('index.jo')))


@bp.route('/neu', methods=('GET','POST'))
def neustart():
    db = get_db()
    game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
    db.execute("UPDATE game SET run = 0 WHERE run = 1")
    db.commit()
    return redirect(url_for('spiele.startgame'))