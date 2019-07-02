URL = "https://stratos.blob.core.windows.net/netcdf"

# Create the BlockBlockService that is used to call the Blob service for the storage account.
block_blob_service = BlockBlobService(account_name = 'accountname', account_key = 'accountkey') 

# List the blobs in the container.
print("\nList blobs in the container")
generator = block_blob_service.list_blobs(container_name)
for blob in generator:
    print("\t Blob name: " + blob.name)

# Download the blob(s).
# Add '_DOWNLOADED' as prefix to '.txt' so you can see both files in Documents.
full_path_to_file2 = os.path.join(local_path, string.replace(local_file_name, '.nc', '_DOWNLOADED.txt'))
print("\nDownloading blob to " + full_path_to_file2)
block_blob_service.get_blob_to_path(container_name, local_file_name, full_path_to_file2)