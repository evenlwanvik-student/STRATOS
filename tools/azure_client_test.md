# Testing Azure Blob Client (ABS) time and memory expenses

The tests were executed on a virtual machine with ~3-4Mb memory and 2 cores.

Have a look at ```data/README``` for a better overview of the state of the blob client initialization and indexing process.

## Initializing the azure blob storage client:

### Test 1
This test was performed 09.07.2019. The compressor and memory of the z-array storage client are the same for each chunking combination. The initialization of the client does not seem to be the problem. The issue seems to be opening the z-array as a x-array dataset ("z-x array" below).

 compressor | memory | init-time | z-x array  |   Zarr file     | Comment        |
|:------------:|:-------------:|:-------:|:--------:|:------------------:|--------------------------------------|
      i4        | 64  | ~ 0.004 s | 10.1642 s | chunked-time&depth | chunk={72,30,98,97}  |
              |   |       | 11.2816 s |  chunk-test-1 | chunk={1,1,294,291} |  
              |   |       | 0.9052 s | auto-chunked | chunk={16,15,10,10}   | 

### Test 2
Same as last time, but this time we did a more comprehensive job by doing 100 samples and averaging. The result was that the chunk size didn't seem to affect the creation of a xarray dataset too much. The only extreme measurement was when we tried the blob with the smalles chunk sizes. Other than that, the execution time seems to hit a threshold at about 7-8 seconds. For the next test we will try to either find a better method than xarray, or try to only open subsets with xarray.

The most promising chunk configuration was when chunking with respect to time and depth, i think this gave the best results because it produces relatively large chunk sizes, which is shown in benchmarks to be where compression works best.

 compressor | memory | init-time | z-x array  |   Zarr file     | Comment        |
|:------------:|:-------------:|:-------:|:--------:|:------------------:|--------------------------------------|
      i4        | 64  | 0.000183 s | 8.308415 s | chunk-test-1 | chunk={16,15,10,10}  |
             | |   |   0.000193 s   | 10.342802 s |  chunk-test-2 | chunk={4,3,30,30} |  
             | |   |   0.000165 s    | 31.168953 s | chunk-test-3 | chunk={4,3,7,7}   |
            ||   |   0.00164 s  | 7.473396 s | chunked-time&depth | chunk={1,1,294,291}   | 
            ||   | 0.00165 s  | 8.003488 s | chunked-time&depth | chunk={1,1,294,291} | 

