import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(UPDATE) Updating a Player...')

    # Configuring database connection
    players_container = setup(True, False)[0]

    # Retrieving Player information
    player = req.get_json()
    for feature in player:
        logging.info('(UPDATE) ' + feature + ': ' + str(player[feature]))
    uname = player['username']
    passwd = player['password']

    try:
        user = players_container.read_item(uname, uname)
        logging.info('(UPDATE) ' + uname + ' found in DB')

        # Check password
        if user['password'] != passwd:
            logging.info('(UPDATE) Incorrect password')
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "wrong password" }),
            status_code = 400) 

        updated_user = {}
        if 'add_to_games_played' in player and 'add_to_score' in player:
            add_games = player['add_to_games_played']
            add_score = player['add_to_score']
            logging.info('(UPDATE) Updating Score by ' + str(add_score) + ' and Games Played by ' + str(add_games))

            # Check for valid score/games
            if add_games <= 0 or add_score <= 0:
                logging.info('(UPDATE) Incorrect paramater : No negatives')
                return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0" }),
                status_code = 400)
                
            for feature in user:
                if feature == 'games_played' or feature == 'total_score':
                    updated_user[feature] = user[feature] + add_games
                else:
                    updated_user[feature] = user[feature]

        else:
            if 'add_to_games_played' in player:
                add_games = player['add_to_games_played']
                logging.info('(UPDATE) Updating Games Played by ' + str(add_games))

                # Check for valid games
                if add_games <= 0:
                    logging.info('(UPDATE) Incorrect paramater : No negatives')
                    return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0" }),
                    status_code = 400)

                for feature in user:
                    if feature == 'games_played':
                        updated_user[feature] = user[feature] + add_games
                    else:
                        updated_user[feature] = user[feature]
    
            if 'add_to_score' in player:
                add_score = player['add_to_score']
                logging.info('(UPDATE) Updating Score by ' + str(add_score))

                # Check for valid games
                if add_score <= 0:
                    logging.info('(UPDATE) Incorrect paramater : No negatives')
                    return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0" }),
                    status_code = 400)

                for feature in user:
                    if feature == 'total_score':
                        updated_user[feature] = user[feature] + add_score
                    else:
                        updated_user[feature] = user[feature]

        # Update the DB
        try:
            players_container.replace_item(uname, updated_user)
            logging.info('(UPDATE) User updated successfully!')
            return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
            status_code = 200)
        except exceptions.CosmosHttpResponseError:
            logging.info('(UPDATE) User not found in DB')
            return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'user does not exist'}),
            status_code = 400)

    except exceptions.CosmosHttpResponseError:
        logging.info('(UPDATE) User not found in DB')
        return func.HttpResponse(body=json.dumps({'result': False , 'msg': 'user does not exist'}),
        status_code = 400)
    