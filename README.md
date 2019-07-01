# Stratos

Visualizing netCDF files from SINMOD, OSCAR and DREAM on a web page.

This is a temporary structure for displaying a single netcdf file in web page.

* To start the server in a container: sudo bash start.sh
* Check for existing images in the container: sudo docker ps -a
* To stop and remove existing images: sudo bash stop.sh

todo: 
* Insert dependencies into requirements: xarray, scipy, json, numpy

```python
from azure.storage.blob import BlockBlobService
storage = BlockBlobService(account_name='myname', account_key = 'mykey')
file = storage.get_blob_to_stream('accountname','blobname','stream')
df = pd.read_csv(file)
```

1. block blobs and web-server on same storage account, just in different containers?
2. Since it is a block blob, do we have to stream the full blob to the web-server container?
3. Copy the blob locally or ?

https://stackoverflow.com/questions/54408738/how-to-use-get-file-properties-rest-api-for-azure-files-storage-using-python
https://stackoverflow.com/questions/49467961/python-script-to-use-data-from-azure-storage-blob-by-stream-and-update-blob-by

Authors: Even Wanvik and Maria Skårdal
