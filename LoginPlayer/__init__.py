import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(LOGIN) Logging in a Player')

    # Configuring database connection
    players_container = setup(True, False)[0]

    # Retrieving Player information
    player = req.get_json()
    uname = player['username']
    passwd = player['password']
    logging.info('(LOGIN) Username: ' + uname + ' Password: ' + passwd)

    try:
        # Check if both username and correct password are registered
        user = players_container.read_item(uname, uname)
        if user['password'] == passwd:
            logging.info('(LOGIN) User found in DB')
            return func.HttpResponse(body=json.dumps({'result': True , 'msg': 'OK'}),
            status_code = 200)
        
        logging.info('(LOGIN) Incorrect password: Login failed')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Username or password incorrect'}),
        status_code = 400)

    except exceptions.CosmosHttpResponseError:
        logging.info('(LOGIN) No entry in DB')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Username or password incorrect'}),
        status_code = 400)