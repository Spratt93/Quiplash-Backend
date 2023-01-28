import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(REGISTER) Registering a player...')
    
    # Configuring database connection
    players_container = setup(True, False)[0]
    logging.info('(REGISTER) Setup DB connection successfully')

    # Retrieving Player information
    player = req.get_json()
    uname = player['username']
    passwd = player['password']
    logging.info('(REGISTER) Username: ' + uname + ' Password: ' + passwd)


    # Check length of the username and password
    uname_length = len(uname)
    psswd_length = len(passwd)
    if uname_length < 4 or uname_length > 16:
        logging.info('(REGISTER) Username is of incorrect length')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Username less than 4 characters or more than 16 characters'}),
            status_code = 400)
    if psswd_length < 8 or psswd_length > 24:
        logging.info('(REGISTER) Password is of incorrect length')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Password less than 8 characters or more than 24 characters'}),
            status_code = 400)

    # Query the database
    try:
        # Check if username already exists
        players_container.read_item(uname,uname)
        logging.info('(REGISTER) Entry found in DB')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Username already exists'}),
        status_code = 400)
    except exceptions.CosmosResourceNotFoundError:
        logging.info('(REGISTER) No entry in DB')

        # insert username
        translated_player = {}
        for feature in player:
            if feature == 'username':
                translated_player['id'] = player[feature]
            else:
                translated_player[feature] = player[feature]
        translated_player['games_played'] = 0
        translated_player['total_score'] = 0
        
        try:
            players_container.create_item(body=translated_player)
            logging.info('(REGISTER) Added username to the DB')
            return func.HttpResponse(body=json.dumps({'result': True , 'msg': 'OK'}),
            status_code = 200)
        except exceptions.CosmosHttpResponseError:
            logging.info('(REGISTER) Error when inserting into the DB, Stack trace printed below')
            return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'Username already exists'}),
            status_code = 400)

    
   
        