import logging
import json
import random
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(GET) Fetching prompts...')

    # Configuring database connection
    db_setup = setup(True, True)
    players_container = db_setup[0]
    prompts_container = db_setup[1]

    # Get parameters
    prompts = req.get_json()
    is_prompts = False
    if 'prompts' in prompts:
        n = prompts['prompts']
        logging.info('(GET) Return ' + str(n) + ' prompts')
        is_prompts = True
    else:
        players = prompts['players']
        logging.info('(GET) Return all prompts created by players ' + str(players))

    # Return n random prompts
    # Currently dont have try except cos error protocol not specified
    return_list = []
    if is_prompts:
        db_size_query = 'SELECT VALUE COUNT(1) FROM Prompts' 
        res = prompts_container.query_items(db_size_query, enable_cross_partition_query=True)
        for r in res:
            db_size = r
            logging.info('(GET) DB size = ' + str(db_size))

        all_prompts = list(prompts_container.read_all_items())
        if n > db_size:
            logging.info('(GET) Returning all items')
            all_prompts = prompts_container.read_all_items()
            for prompt in all_prompts:
                new_prompt = {}
                new_prompt['id'] = prompt['id']
                new_prompt['text'] = prompt['text']
                new_prompt['username'] = prompt['username']
                return_list.append(new_prompt)
        else:
            logging.info('(GET) Returning ' + str(n) + ' random items')
            rand_list = random.sample(range(0, db_size-1), n)
            for ran in rand_list:
                rand_prompt = all_prompts[ran]
                new_prompt = {}
                new_prompt['id'] = rand_prompt['id']
                new_prompt['text'] = rand_prompt['text']
                new_prompt['username'] = rand_prompt['username']
                return_list.append(new_prompt)
    
    # return prompts from a list of given users
    else:
        for player in players:
            # make sure player exists
            try:
                players_container.read_item(player, player)
                get_prompts_query = 'SELECT * FROM Prompts WHERE Prompts.username="{0}"'.format(player)
                get_prompts = prompts_container.query_items(get_prompts_query, enable_cross_partition_query=True)
                for item in get_prompts:
                    new_prompt = {}
                    new_prompt['id'] = item['id']
                    new_prompt['text'] = item['text']
                    new_prompt['username'] = item['username']
                    return_list.append(new_prompt)
            except exceptions.CosmosHttpResponseError:
                logging.info('(GET) Invalid username, onto next username')

    logging.info('(GET) Return list ' + str(return_list))
    return func.HttpResponse(body=json.dumps(return_list), status_code=200)