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
    for element in db.execute('SELECT * FROM einsatz WHERE spiel_id = ?',(game['id'],)):
        alleEinsaetze.append(element[2])
        users.append(element[3])

    '''    
    DEBUG
    print(len(alleEinsaetze), file=sys.stdout)
    print(len(users), file=sys.stdout)
    for i in range(len(alleEinsaetze)):
        print(i,file=sys.stdout)
        print("user: " + str(users[i]) + " hat gesetzt: " + str(alleEinsaetze[i]), file=sys.stdout )
    print("hier", file=sys.stdout)
    '''
    looser_id = random.choices(users,alleEinsaetze)
    looser_name = db.execute('SELECT * FROM user WHERE id = ?', (looser_id[0],)).fetchone()
    return render_template('looser.html', looser=looser_name[1])


@bp.route('/start', methods=('GET','POST'))
@login_required
def startgame():
    db = get_db()
    db.execute("INSERT INTO game (name,run) VALUES(?,?)",("sauf","1"))
    db.commit()
    return(redirect(url_for('index.jo')))