import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(DELETE) Deleting a prompt...')

    # Configuring database connection
    db_setup = setup(True, True)
    players_container = db_setup[0]
    prompts_container = db_setup[1]

    # Get parameters
    prompt = req.get_json()
    prompt_id = str(prompt['id'])
    uname = prompt['username']
    passwd = prompt['password']
    logging.info('(DELETE) ID: ' + prompt_id + ' Username: ' + uname + ' Password: ' + passwd)

    # Check that prompt id exists
    try:
        prompt_read = prompts_container.read_item(prompt_id, prompt_id)
        logging.info('(DELETE) Prompt ID ' + prompt_id + ' found')
    except exceptions.CosmosResourceNotFoundError:
        logging.info('(DELETE) Prompt ID ' + prompt_id + ' not found')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt id does not exist" }),
        status_code=400)
    
    # Check for bad username or password
    try:
        player_read = players_container.read_item(uname, uname)
    except exceptions.CosmosResourceNotFoundError:
        logging.info('(DELETE) Username ' + uname + ' does not exist')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
        status_code=400)

    if player_read['password'] != passwd:
        logging.info('(DELETE) Password incorrect')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
        status_code=400)

    # Check for access denied
    if prompt_read['username'] != uname:
        logging.info('(DELETE) Access Denied for ' + uname)
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "access denied" }),
        status_code=401)

    # Delete the prompt
    try:
        prompts_container.delete_item(prompt_id, prompt_id)
    except exceptions.CosmosHttpResponseError:
        logging.info('(DELETE) Error when deleting Prompt ' + prompt_id)
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "access denied" }),
        status_code=401)

    logging.info('(DELETE) Prompt ' + prompt_id + ' deleted successfully')
    return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),
    status_code=200)