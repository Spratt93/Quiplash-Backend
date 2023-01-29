# Quiplash Backend

## HTTP triggered Azure Functions for logic of Quiplash

You must also create a **config.py** file that includes the details listed below in JSON format.

Function App:

- Local URI
- Cloud URI

CosmosDB:

- URI
- Primary key
- id
- Container names

Testing:

- `python -m venv {venv_name}` to create virtual environment
- `pip install azure-functions` to get CLI tools
- `func init {function_app_name} --python` to create the local dev function app
- `func start` hosts the Azure Functions locally

