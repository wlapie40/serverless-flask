from flask import Blueprint, render_template
import logging

blueprint = Blueprint('main', __name__)
log = logging.getLogger(__name__)


@blueprint.route('/')
def index():
    return render_template('base.html')


@blueprint.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
