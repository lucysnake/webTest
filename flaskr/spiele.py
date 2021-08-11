import functools
import sys
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

        #User submits anzahl
        if request.method == 'POST':
            return gesetzt()
        
        #get username
        user_id = session.get('user_id')
        g.user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        return(render_template('shot.html', username = g.user[1]))

 
def gesetzt():
    #get anzahl from HTML
    anz = request.form['anz']

    #get user_id
    user_id = session.get('user_id')

    #insert into Einsatz
    db = get_db()
    game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
    db.execute("INSERT INTO einsatz (spiel_id,anzahlEinsatz,spieler_id) VALUES(?,?,?)",(game['id'],anz,user_id))
    return render_template('gesetzt.html',anz=anz)


# Spiel mit game_id auswerten, Einsätze zusammenzählen, Wahrscheinlichkeiten berechenen, Game Attribut run auf 0 setzen
def auswerten():
    print("hier", file=sys.stdout)
    db = get_db()
    game = db.execute('SELECT * FROM game WHERE run = 1').fetchone()
    einsaetze = db.execute('SELECT * FROM einsatz WHERE spiel_id = ?',(game['game_id'],)).fetchall()
    print(einsaetze, file=sys.stdout)


@bp.route('/start', methods=('GET','POST'))
@login_required
def startgame():
    db = get_db()
    db.execute("INSERT INTO game (name,run) VALUES(?,?)",("sauf","1"))
    db.commit()
    return(redirect(url_for('index.jo')))