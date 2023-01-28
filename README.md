### Quiplash Backend

## Azure Functions for logic of Quiplash (https://github.com/Spratt93/Quiplash)

### To test locally install the Azure CLI tools

You must also create a **config.py** file that includes the details listed below in JSON format.

Function App:

- Local URI
- Cloud URI

CosmosDB:

- URI
- Primary key
- id
- Container names

Then run the following to host the Azure Functions locally

`func start`
