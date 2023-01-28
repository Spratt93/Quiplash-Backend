import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import random
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(CREATE) Creating a prompt...')

    # Configuring database connection
    db_setup = setup(True, True)
    players_container = db_setup[0]
    prompts_container = db_setup[1]

    # Get parameters
    prompt = req.get_json()
    text = prompt['text']
    uname = prompt['username']
    passwd = prompt['password']
    logging.info('(CREATE) Username: ' + uname + ' Password: ' + passwd + ' text: ' + text)

    # Check prompt has valid length
    if len(text) < 20 or len(text) > 100:
        logging.info('(CREATE) Prompt has incorrect length')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or > 100 characters" }),
        status_code = 400)

    # Check correct username and password
    try:
        user = players_container.read_item(uname, uname)
        if user['password'] != passwd:
            logging.info('(CREATE) Password is incorrect')
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
            status_code=400)
        
        # Check that user has not previously created the prompt
        prompt_query = 'SELECT * FROM Prompts WHERE Prompts.username="{0}" AND Prompts.text="{1}"'.format(uname, text)
        logging.info('(CREATE) query=' + prompt_query)
        try:
            prompt_query = prompts_container.query_items(prompt_query, enable_cross_partition_query=True)
            prompt_count = 0
            for q in prompt_query:
                prompt_count += 1
            if prompt_count > 0:
                logging.info('(CREATE) Prompt already exists for given user') 
                return func.HttpResponse(body=json.dumps({"result": False, "msg": "This user already has a prompt with the same text"}),
                status_code=403)
            else:
                logging.info('(CREATE) Prompt not previously created')
                new_prompt = {}
                does_exist = True
                # Generate rand int -> check not already in DB
                while (does_exist):
                    unique_id = random.randint(1, 50000000000000)
                    try:
                        prompts_container.read_item(str(unique_id), str(unique_id))
                        logging.info('(CREATE) ID already exists, generating new one')
                    except exceptions.CosmosHttpResponseError:
                        logging.info('(CREATE) Unique ID generated successfully ' + str(unique_id))
                        does_exist = False
                new_prompt['id'] = str(unique_id)
                new_prompt['username'] = uname
                new_prompt['text'] = text
                try:
                    prompts_container.create_item(new_prompt)
                    logging.info('(CREATE) Added Prompt to DB successfully')
                    return func.HttpResponse(body=json.dumps({"result" : True, "msg" : "OK" }),
                    status_code=200) 
                except exceptions.CosmosHttpResponseError:
                    logging.info('(CREATE) Issue when inserting into DB')
                    return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
                    status_code=400) 

        except exceptions.CosmosHttpResponseError as e:
            logging.info('(CREATE) Username has not been registered')
            print(e.message)
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
            status_code=400)      
    
    except exceptions.CosmosHttpResponseError:
        logging.info('(CREATE) Username has not been registered')
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),
        status_code=400)