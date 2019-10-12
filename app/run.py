import os
from datetime import datetime

import flask_login
import requests
from config.config import get_config
from flask import (session,
                   redirect,
                   request,
                   render_template,
                   url_for,
                   )
from http_handler import create_app
from jose import jwt
from requests.auth import HTTPBasicAuth
from pprint import pprint

config = get_config()
app = create_app(config)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)



class User(flask_login.UserMixin):
    """Standard flask_login UserMixin"""
    email = None


@login_manager.user_loader
def user_loader(session_token):
    """Populate user object, check expiry"""
    if "expires" not in session:
        return None

    expires = datetime.utcfromtimestamp(session['expires'])
    if (expires - datetime.utcnow()).total_seconds() < 0:
        return None

    user = User()
    user.id = session_token
    user.email = session['email']

    return user


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route("/login")
def login():
    """ Login route """
    # https://docs.aws.amazon.com/en_pv/cognito/latest/developerguide/login-endpoint.html

    session['csrf_state'] = os.urandom(8).hex()
    url = f"{config.AWS_COGNITO_DOMAIN}/login?response_type=code&" \
          f"client_id={config.AWS_COGNITO_CLIENT_ID}&" \
          f"state={session['csrf_state']}&" \
          f"redirect_uri={config.AWS_COGNITO_REDIRECT}"
    return redirect(url)


@app.route("/logout")
def logout():
    """Logout route"""
    # https://docs.aws.amazon.com/en_pv/cognito/latest/developerguide/logout-endpoint.html
    flask_login.logout_user()
    # cognito_logout = f"https://{config.AWS_COGNITO_DOMAIN}/logout?response_type=code&client_id={config.AWS_COGNITO_CLIENT_ID}&logout_uri=https://127.0.0.1:{config.PORT}/"
    cognito_logout = f"https://{config.AWS_COGNITO_DOMAIN}/logout?" \
    f"client_id={config.AWS_COGNITO_CLIENT_ID}&" \
    f"logout_uri=http://localhost:8080/"
    return redirect(cognito_logout)


@app.route("/callback")
def callback():
    """Exchange the 'code' for Cognito tokens"""
    #https://docs.aws.amazon.com/en_pv/cognito/latest/developerguide/token-endpoint.html
    csrf_state = request.args.get('state')
    code = request.args.get('code')

    url = f"{config.AWS_COGNITO_DOMAIN}/oauth2/token"
    data = {
            'grant_type': 'authorization_code',
            'client_id': config.AWS_COGNITO_CLIENT_ID,
            'code': code,
            "redirect_uri": config.AWS_COGNITO_REDIRECT
            }

    auth = HTTPBasicAuth(
        config.AWS_COGNITO_CLIENT_ID,
        config.AWS_COGNITO_SECRET
        )
    response = requests.post(url=url, data=data, auth=auth)

    #https://docs.aws.amazon.com/en_pv/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
    print(f"[callback] request: {request}")
    # print(f"[callback] csrf_state: {csrf_state}")
    # print(f"session['csrf_state']: {session['csrf_state']}")
    # if response.status_code == requests.codes.ok and csrf_state == session['csrf_state']:
    if response.status_code == requests.codes.ok:
        verify(response.json()["access_token"])
        id_token = verify(response.json()["id_token"], response.json()["access_token"])
        print(f"{verify(response.json()['access_token'])}")
        print(f"id_token {pprint(id_token) }")

        user = User()
        user.id = id_token["cognito:username"]
        session['email'] = id_token["email"]
        session['expires'] = id_token["exp"]
        session['refresh_token'] = response.json()["refresh_token"]
        flask_login.login_user(user, remember=False)

        return redirect(url_for("index"))
    return render_template("error.html")


def well_known_jwks():
    ### load and cache cognito JSON Web Key (JWK)
    # https://docs.aws.amazon.com/en_pv/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
    url = (f"https://cognito-idp.{config.AWS_REGION}.amazonaws.com/{config.AWS_COGNITO_POOL_ID}/.well-known/jwks.json")
    jwks = requests.get(url).json()["keys"]
    return jwks


def verify(token, access_token=None):
    """Verify a cognito JWT"""
    # get the key id from the header, locate it in the cognito keys
    # and verify the key
    jwks = well_known_jwks()

    header = jwt.get_unverified_header(token)
    key = [k for k in jwks if k["kid"] == header['kid']][0]
    id_token = jwt.decode(token, key, audience=config.AWS_COGNITO_CLIENT_ID, access_token=access_token)
    return id_token


if __name__ == '__main__':
    app.run(port=config.PORT, threaded=True)
