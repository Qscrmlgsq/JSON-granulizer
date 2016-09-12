import json
import argparse
import os
import errno


def ensure_list(object):
    """
    :returns: object if object was a list; otherwise it returns [object].
    """
    if isinstance(object, list):
        return object
    else:
        return [object]


def ensure_dir(path):
    """
    creates a dir at path if one doesn't already exist
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_source_files(sourcepath, recurse = False):
    """
    checks if a sourcepath is a file or directory
    :returns: a list of all json files at the source (if file is not json or dir contains no json then it returns an empty list)
    """
    if os.path.isfile(sourcepath) and sourcepath.endswith('.json'):
        return ensure_list(sourcepath)
    elif os.path.isdir(sourcepath):
        if recurse:
            walk = os.walk(sourcepath)
            return_files = []
            for dir in walk:
                dir_path = dir[0]
                return_files += [os.path.join(dir_path,file) for file in dir[2] if file.endswith('.json')]
            return return_files
        else:
            return [os.path.join(sourcepath,file) for file in os.listdir(sourcepath) if file.endswith('.json')]
    else:
        return []


def parse_args():
    """
    parse command line arguments and check that their values are valid
    :returns: an object containing all argument values
    """
    parser = argparse.ArgumentParser(description='Split json files into new files each containing a given number of json objects')
    parser.add_argument('source', default='', help='the source file path of the json file or directory containing files')
    parser.add_argument('destination', default='', help='the path to the directory to store the new json files')
    parser.add_argument('grain', default='1', help='the number of json objects to be put in each file, grain size 0 means combine all files')
    parser.add_argument('-n', '--name', default='json_grain', help='Name of new json files')
    parser.add_argument('-r', '--recurse', action='store_true', help='Recurse through all subdirectories')
    parser.add_argument('-v', '--verbosity', action='count', default=0, help='increase output verbosity (2 levels)')
    args = parser.parse_args()

    #check arguments are valid
    if not args.source:
        raise ValueError("No source path supplied.")
    if not args.destination:
        raise ValueError("No destination directory supplied.")
    if not args.grain:
        raise ValueError("No grain supplied.")
    if not args.name:
        raise ValueError("No name supplied.")

    return args


def write_new_json(args,source_files):
    """
    read json from source_files, split it and write it to the destination, split into the required grain size
    """
    json_write_buffer = [] #the list of json to write to file
    new_file_num = 0 #the number of new files
    current_json_num = 0 #the current json num  
    total_files = len(source_files)

    for index, filepath in enumerate(source_files):
        if args.verbosity >= 1:
            print 'using file {} of {}'.format(index+1, total_files)
        if args.verbosity >= 2:
            print os.path.abspath(filepath)

        with open(filepath, 'r') as file: #expects file to be a list of json items
            file_data = ensure_list(json.loads(file.read()))

        for current_json in file_data:
            if args.grain and current_json_num % args.grain == 0 and json_write_buffer:
                new_file_path = os.path.join(args.destination, args.name + str(new_file_num) + '.json')
                with open(new_file_path,'a') as new_file:
                    if args.verbosity >= 1:
                        print 'creating new file {}'.format(new_file_num)
                    if args.verbosity >=2:
                        print os.path.abspath(new_file_path)
                    new_file.write(json.dumps(json_write_buffer))
                new_file_num += 1
                json_write_buffer = []
            json_write_buffer.append(current_json)
            current_json_num += 1

    #get the dregs (or everything if args.grain is 0)
    if json_write_buffer:
        new_file_path = os.path.join(args.destination, args.name + str(new_file_num) + '.json')
        with open(new_file_path,'a') as new_file:
            if args.verbosity >= 1:
                print 'creating new file {}'.format(new_file_num)
            if args.verbosity >=2:
                print os.path.abspath(new_file_path)
            new_file.write(json.dumps(json_write_buffer))


if __name__ == '__main__':
    args = parse_args()
    ensure_dir(args.destination)
    source_files = get_source_files(args.source, args.recurse)

    #check setup
    try:
        args.grain=abs(int(args.grain))
    except ValueError:
        raise ValueError("The grainsize is not an integer.")
    if not source_files:
        raise RuntimeError("No json source files at the given source path. Exiting.")
    if not os.path.isdir(args.destination):
        raise RuntimeError("Not able to create/identify directory at given destination path. Exiting.")

    write_new_json(args, source_files)