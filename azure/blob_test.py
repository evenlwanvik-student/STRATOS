from azure.storage.blob import BlockBlobService
import time

from azure import *
from azure.storage import *

#from azure.storage.blob import (
#    ContentSettings,
#    BlobBlock,
#    BlockListType,
#)

t1=time.time()

# Create the BlockBlockService that is used to call the Blob service for the storage account.
account_name = 'stratos'
access_key = 'A7nrOYKyq6y2GLlprXc6tmd+olu50blx4sPjdH1slTasiNl8jpVuy+V0UBWFNmwgVFSHMGP2/kmzahXcQlh+Vg=='
blob_service = BlockBlobService(account_name=account_name, account_key=access_key) 

container_name = 'zarr'
blob_service


# List the blobs in the container.

print("\nList blobs in the container " + container_name + ":")
generator = blob_service.list_blobs(container_name)
for blob in generator:
    print("\t Blob name: " + blob.name)

# Download blob to a stream, returns an instance of the blob with properties and metadata
blob_name = 'Franfjorden32m/samples_NSEW_2013.03.11.nc'





with open('blob_test.txt', 'w+') as fp:
    #blob = blob_service.get_blob_to_stream(
        container_name, 
        blob_name, 
        fp)
    #content_length = blob.properties.content_length

    print blob

t2=time.time()
print("The whole thing took %s seconds " % (t2 - t1))

#with open(file_path, 'w+') as file:
    #blob = block_blob_service.get_blob_to_stream(container_name=container_name, blob_name=blob_name, stream=file, max_connections=2) 