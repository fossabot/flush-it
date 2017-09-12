#----------------------------------------------------------------------------#
# APP CONFIGURATION
#----------------------------------------------------------------------------#

# standard library imports

import os
import logging
from logging import Formatter, FileHandler
#import requests
import json

# dependencies
from flask import Flask, render_template, request, make_response, session
#import pdb

# config
app = Flask(__name__)
app.config.from_pyfile('config.py')

#----------------------------------------------------------------------------#
# Helper Functions & Wrappers
#----------------------------------------------------------------------------#

def get_ags_token(session,token_name,username,password,client,referer):
    """Requests and ArcGIS Server Token
    session: pass flask session object in
    token_name: string, used to store token in session
    other params are ArcGIS Server params
    """
    if token_name not in session:
        params = {
            'username': username,
            'referer': referer,
            'password': password, 
            'client': client,
            'f': 'json'
        }
        response = requests.post(
            app.config['ROK_AUTH_URL'],
            data=params
        )
        token = response.json()
        session[token_name] = token
        print("{0} token acquired: {1}".format(token_name, token))
        return token
    else:
        print("Using existing {0} token: {1}".format(token_name, session[token_name]))
        return session[token_name]
    
'''
def get_agol_token():
    """requests and returns an ArcGIS Token for the pre-registered application.
    Client id and secrets are managed through the ArcGIS Developer's console:
        https://developers.arcgis.com/applications/#/ca3136177e564894907ddff85c325529/
        (CivicMapper AGOL organization credentials required)
    """
    params = {
        'client_id': app.config['ESRI_APP_CLIENT_ID'],
        'client_secret': app.config['ESRI_APP_CLIENT_SECRET'],
        'grant_type': "client_credentials"
    }
    request = requests.get(
        'https://www.arcgis.com/sharing/oauth2/token',
        params=params
    )
    token = request.json()
    print("token acquired: {0}".format(token))
    return token
'''
#----------------------------------------------------------------------------#
# Controllers / Route Handlers
#----------------------------------------------------------------------------#

# ---------------------------------------------------
# pages (rendered from templates)
## map view
@app.route('/')
def main():
    return render_template('pages/index.html')

@app.route('/token/')
def token():
    trace_token = get_ags_token(session,'trace_token', app.config['ROK_USER'],app.config['ROK_PW'],app.config['ROK_REFERER_URL'],app.config['ROK_CLIENT_TYPE'])
    data_token = get_ags_token(session, 'data_token', app.config['CMG_USER'],app.config['CMG_PW'],app.config['CMG_REFERER_URL'],app.config['CMG_CLIENT_TYPE'])
    return {"trace_token":trace_token,"data_token":data_token}

# ------------------------------------------------
# Error Handling

## Error handler 500
@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

## Error handler 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

## Error Logging
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')