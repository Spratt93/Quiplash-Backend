import logging
import json
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
from DBSetup import setup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('(GET_TEXT) Fetching prompt text...')

    # Configuring database connection
    prompts_container = setup(False, True)[0]

    # Get parameters
    req_json = req.get_json()
    is_exact = req_json['exact']
    word = req_json['word']
    logging.info('(GET_TEXT) Exact search = ' + str(is_exact) + ' where word = ' + word)

    search_res = prompts_container.query_items(query = """
        SELECT Prompts.id, Prompts.text, Prompts.username
        FROM Prompts
        WHERE RegexMatch (Prompts.text, @word, @case)
        """,
        parameters=[
          {"name": "@word", "value": f'\\b{req_json["word"]}\\b'},
          {"name": "@case", "value": "" if req_json["exact"] else "i"}
        ],
        enable_cross_partition_query=True)
    return_list = []

    for res in search_res:
        logging.info('(GET_TEXT) Exact match for word = ' + word)
        return_list.append(res)

    logging.info('(GET_TEXT) Return list ' + str(return_list))
    return func.HttpResponse(body=json.dumps(return_list), status_code=200)
