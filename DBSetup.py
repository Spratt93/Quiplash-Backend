import os
import config
import azure.cosmos as cosmos

def setup(for_players, for_prompts):
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'])
    db_client = client.get_database_client(config.settings['db_id'])

    # Configure containers
    if for_players and for_prompts:
        players_container = db_client.get_container_client('Players')
        promptscontainer = db_client.get_container_client('Prompts')
        return [players_container, promptscontainer]

    if for_players:
        players_container = db_client.get_container_client('Players')
        return [players_container]

    if for_prompts:
        promptscontainer = db_client.get_container_client('Prompts')
        return [promptscontainer]