
from azure.storage.blob import BlockBlobService
import logging
import warnings
import time

def get_json_blob(blob_name):
    ''' This function fetches and returns a pregenerated json object that is stored as a blob in azure. '''
    BLOB_NAME = blob_name
    CONTAINER_NAME  = 'json'
    ACCOUNT_NAME    = 'stratos'
    ACCOUNT_KEY     = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='

    start=time.time()
    block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
    logging.warning('Getting json blob...')
    jsonData = block_blob_service.get_blob_to_text(CONTAINER_NAME, BLOB_NAME)
    end=time.time()
    logging.warning("execution time retrieving JSON blob: %f", end-start)
    return (jsonData.content)



