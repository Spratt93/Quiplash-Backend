import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(LEADERBOARD) Displaying Leaderboard...')

    # Configuring database connection
    players_container = setup(True, False)[0]

    player = req.get_json()
    leaderboard_size = player['top']
    query = 'SELECT TOP ' + str(leaderboard_size) + ' * FROM Players ORDER BY Players.total_score DESC, Players.id ASC'
    logging.info('(LEADERBOARD) ' + query)

    try:
        results = players_container.query_items(query, enable_cross_partition_query=True)
        logging.info('(LEADERBOARD) DB queried successfully')
        out = []
        for result in results:
            out_json = {}
            out_json['username'] = result['id']
            out_json['score'] = result['total_score']
            out_json['games_played'] = result['games_played']
            logging.info('(LEADERBOARD) ' + str(out_json))
            out.append(out_json)

        return func.HttpResponse(body=json.dumps(out), status_code = 200)
    
    except exceptions.CosmosHttpResponseError:
        logging.info('(LEADERBOARD) Error when querying DB')
        return func.HttpResponse(body=json.dumps({'Error' : 'DatabaseError'}), status_code = 400)