# JSON-granulizer
A script for splitting a list of JSON objects into smaller files of a given granularity, run from the command line with additional arguments

usage: json_granuliser.py [-h] [-n NAME] [-r] [-v] source destination grain

Split json files into new files each containing a given number of json objects

positional arguments:  
  source - The source file path of the json file or directory containing files  
  destination - The path to the directory to store the new json files  
  grain - The number of json objects to be put in each file, grain size 0 means combine all files  

optional arguments:  
  -h, --help - Show this help message and exit  
  -n NAME, --name NAME - Name of new json files  
  -r, --recurse - Recurse through all subdirectories  
  -v, --verbosity - Increase output verbosity (2 levels)  
