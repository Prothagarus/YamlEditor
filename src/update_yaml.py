import sys
import ruamel.yaml
from  ruamel.yaml import YAML
import argparse
def update_yaml_element(yaml_data, path_value_pairs):
    """
    Update multiple nested elements in a YAML data structure.
    
    :param yaml_data: The YAML data structure to update.
    :param path_value_pairs: A list of tuples, where each tuple contains a path and a new value.
    """
    for path, new_value in path_value_pairs:
        if isinstance(path, str):
            path = path.split(':')
        
        current_data = yaml_data
        for key in path[:-1]:
            try:
                key = int(key) # Convert to integer if possible
            except ValueError:
                pass # Keep as string if not convertible to integer
            
            current_data = current_data[key]
        
        # Check if the new value is not None or an empty dictionary/list
        if new_value is not None and new_value != {}:
            current_data[path[-1]] = new_value
def print_keys(data, path='', depth=0, max_depth=None):
    """
    Recursively print the paths to all keys in the YAML data structure, focusing on the lowest-level dictionaries.
    
    :param data: The YAML data structure to traverse.
    :param path: The current path being traversed.
    :param depth: The current depth of recursion.
    :param max_depth: The maximum depth to traverse.
    """
    if max_depth is None:
        # Determine the maximum depth by counting the number of keys in the top-level dictionary
        max_depth = len(data) if isinstance(data, dict) else 0

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}:{key}" if path else key
            # If this is the last key in the dictionary, print the path without the value
            if key == list(data.keys())[-1]:
                print_keys(value, new_path, depth=depth+1, max_depth=max_depth)
            else:
                print_keys(value, new_path, depth=depth, max_depth=max_depth)
    elif isinstance(data, list):
        if isinstance(data[0],dict):
            for index, item in enumerate(data):
                if isinstance(data[index],dict):
                    new_path = f"{path}:{index}" if path else str(index)
                # If this is the last item in the list, print the path without the value
                #if index == len(data) - 1:
                    print_keys(item, new_path, depth=depth+1, max_depth=max_depth)
                else:
                    print(path)
        else:
                    print(path)

    else:
        
        # Only print the path if it's at the lowest level
        #if depth == max_depth - 1:
        print(path)
def print_paths(data, path=''):
    """
    Recursively print the paths to all nodes in the YAML data structure.
    
    :param data: The YAML data structure to traverse.
    :param path: The current path being traversed.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value,list) and isinstance(value,dict):
                print (f"{path}:{value}")
            new_path = f"{path}:{key}" if path else key
            print_paths(value, new_path)
    elif isinstance(data, list):
        if not isinstance(data,list) and isinstance(data,dict):
                print(f"{path}:{value}")
        for index, item in enumerate(data):
            new_path = f"{path}:{index}" if path else str(index)
            print_paths(item, new_path)
    else:
        print(path)
def main():
    parser = argparse.ArgumentParser(description='Update a YAML file dynamically with multiple changes.')
    parser.add_argument('file', help='The YAML file to update.')
    parser.add_argument('-p', '--path', nargs='+', help='Paths to the elements to update, separated by colons.')
    parser.add_argument('-v', '--value', nargs='+', help='New values to set for the specified elements.')
    parser.add_argument('-k', '--keyvals', action='store_true', help='show all key values in an input')
    
    parser.add_argument('-o', '--output', action='store', dest='output', help="Directs the output to a name of your choice")
    parser.add_argument('-i','--inputargprint',action='store_true',help="Prints all possible arguments to edit incoming yaml")
    parser.add_argument('--changes-file', action='store', dest='changes_file', help="A YAML file containing the changes to apply.")
    args = parser.parse_args()

    # Initialize the YAML parser
    yamlp = ruamel.yaml.YAML()

    # Load the YAML content
    with open(args.file, 'r') as f:
        data = yamlp.load(f)

    if args.inputargprint:
       print_keys(data)
    if args.keyvals:
       print_paths(data)
       #print_paths(data)
    # Prepare path-value pairs
    path_value_pairs = []
    if args.path and args.value:
        path_value_pairs = list(zip(args.path, args.value))

    # Load and apply changes from the specified YAML file if provided
    if args.changes_file:
        with open(args.changes_file, 'r') as f:
            changes = yamlp.load(f)
            for path, new_value in changes.items():
                path_value_pairs.append((path, new_value))

    # Update the specified elements
    update_yaml_element(data, path_value_pairs)
    # Dump the updated dictionary back to the output file
    if args.output is not None:
        with open(args.output, 'w') as f:
            yamlp.dump(data, f)
    else:
        print("No output file specified. Results will be printed to the console.")
      
        yaml = ruamel.yaml.YAML()
        yaml.dump(data, sys.stdout)
        #out = ruamel.yaml.dump(data)
    

if __name__ == '__main__':
    main()
