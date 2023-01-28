import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(EDIT) Editing a prompt...')

    # Configuring database connection
    db_setup = setup(True, True)
    players_container = db_setup[0]
    prompts_container = db_setup[1]

    # Get parameters
    prompt = req.get_json()
    prompt_id = str(prompt['id'])
    text = prompt['text']
    uname = prompt['username']
    passwd = prompt['password']
    logging.info('(EDIT) ID: ' + prompt_id + ' Username: ' + uname + ' Password: ' + passwd + ' text: ' + text)

    # Check prompt has valid length
    if len(text) < 20 or len(text) > 100:
        logging.info('(EDIT) Prompt has incorrect length')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or >100 characters" }),
        status_code = 400)

    # Check correct username and password
    try:
        user = players_container.read_item(uname, uname)
        if user['password'] != passwd:
            logging.info('(EDIT) Password is incorrect')
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
            status_code=400)
        
        # Check that edited text does not match another prompt by same user
        prompt_query = 'SELECT * FROM Prompts WHERE Prompts.username="{0}" AND Prompts.text="{1}"'.format(uname, text)
        logging.info('(EDIT) query=' + prompt_query)
        try:
            prompt_query = prompts_container.query_items(prompt_query, enable_cross_partition_query=True)
            prompt_count = 0
            for q in prompt_query:
                prompt_count += 1
            if prompt_count > 0:
                logging.info('(EDIT) Prompt already exists for given user') 
                return func.HttpResponse(body=json.dumps({"result": False, "msg": "This user already has a prompt with the same text"}),
                status_code=403)
            else:
                logging.info('(EDIT) Prompt not previously created')
                # Check whether prompt id already exists
                try:
                    upd_prompt = {}
                    upd_prompt['id'] = prompt_id
                    upd_prompt['username'] = uname
                    upd_prompt['text'] = text
                    prompts_container.replace_item(prompt_id, upd_prompt)
                    logging.info('(EDIT) Successfully edited prompt ID: ' + prompt_id)
                    return func.HttpResponse(body=json.dumps({"result": True, "msg": "OK"}),
                    status_code=200)

                except exceptions.CosmosResourceNotFoundError:
                    logging.info('(EDIT) Prompt ID ' + prompt_id + ' does not exist')
                    return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt id does not exist"}),
                    status_code=400) 

        except exceptions.CosmosHttpResponseError:
            logging.info('(EDIT) Query error for Prompt ID: ' + prompt_id)
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
            status_code=400)      
    
    except exceptions.CosmosHttpResponseError:
        logging.info('(EDIT) Username has not been registered')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
        status_code=400)