# MemcLoad 
Multiprocessing version of memc_load.py.<br>
For each log files create process for parsing logs.
Log files info about user's installed apps load to queue.<br>
Create pool of threads for loading info  from queue to memcache store.

### How to run
```
>>> python memc_load_concur.py 
optional arguments:
  -t, --test            # To run protobuf test  
  -l LOG, --log LOG     # Path to log file
  --dry                 # Debug mode
  --pattern PATTERN     # Pattern of files paths, where logs stored
  --idfa IDFA           # Address of IDFA memcache server
  --gaid GAID           # Address of GAID memcache server
  --adid ADID           # Address of ADID memcache server
  --dvid DVID           # Address of DVID memcache server
``` 


