from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import sys
from flaskr.db import get_db

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.spiele import *

bp = Blueprint('index', __name__)


@bp.route('/', methods=('GET', 'POST'))
def jo():
    return render_template('index.html')
