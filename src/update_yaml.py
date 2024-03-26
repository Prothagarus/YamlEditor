import sys
import os
import shutil
import ruamel.yaml
from ruamel.yaml import YAML
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

def apply_changes_and_output(input_file, changes_file, output_dir):
    # Initialize the YAML parser
    yaml = YAML()
    if output_dir is not None:
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)
    # Load the input YAML content
    with open(input_file, 'r') as f:
        data = yaml.load(f)

    # Load the changes YAML content
    with open(changes_file, 'r') as f:
        changes_list = yaml.load(f)
    for case_dict in changes_list['cases']:
        case_value = case_dict['case']
        
        # Apply the changes to the data
        for change_path, change_value in case_dict.items():
            if change_path == 'case':
                continue # Skip the 'case' key as it's not a change
            if change_path == 'output_type':
                output_type = change_value
                continue
            keys = change_path.split(':')
            current_data = data
            for key in keys[:-1]:
                try:
                    key = int(key) # Convert to integer if possible
                except ValueError:
                    pass # Keep as string if not convertible to integer
                current_data = current_data[key]
            current_data[keys[-1]] = change_value    
                
        if output_dir is None:
            print("No output file specified. Results will be printed to the console.")
            print(f"Case_{case_value}:")
            yaml = ruamel.yaml.YAML()
            yaml.dump(data, sys.stdout)

    # Loop through each case in the changes list
        else:
        
        # Create a directory for this case
            if not os.path.exists(os.path.join(output_dir, f"{case_value}")):
                case_dir = os.path.join(output_dir, f"{case_value}")
                os.makedirs(case_dir, exist_ok=True)
            case_dir = os.path.join(output_dir, f"{case_value}")
            # Create subdirectories for output and config
            output_subdir = os.path.join(case_dir, "output")
            config_subdir = os.path.join(case_dir, "config")
            if not os.path.exists(os.path.join(output_subdir, f"{case_value}")):
                os.makedirs(output_subdir, exist_ok=True)
            if not os.path.exists(os.path.join(config_subdir, f"{case_value}")):
                os.makedirs(config_subdir, exist_ok=True)


        # Output the modified data for this case to the specified output file
            # output_file_path = os.path.join(output_subdir, f"{output_type}.yaml")
            # with open(output_file_path, 'w') as f:
            #     yaml.dump(data, f)
            # print(f"Case_{case_value}:")      
            output_file_path = os.path.join(output_subdir, f"{output_type}.yaml")
            with open(output_file_path, 'w') as f:
                yaml.dump(data, f)
            print(f"Modified data for case {case_value} has been written to {output_file_path}\n")

            # Store the portion of the config YAML used to make that output
            config_file_path = os.path.join(config_subdir, f"{output_type}_config.yaml")
            with open(config_file_path, 'w') as f:
                yaml.dump(case_dict, f)
            print(f"Config for case {case_value} has been written to {config_file_path}\n")
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
    parser = argparse.ArgumentParser(description='Apply changes from a YAML file to another and output the result to generated output folder with subfolders containing the changes and the output.')
    parser.add_argument('-i','--input_file',required=True ,help='The input YAML file to modify.')
    parser.add_argument('-c','--changes_file', help='The YAML file containing the changes to apply.')
    parser.add_argument('-o', '--output',  help='The output directory to write the modified data and config to.')
    parser.add_argument('-iap','--inputargprint',action='store_true',help="Prints all possible arguments to edit incoming yaml")
    args = parser.parse_args()
    

    if args.input_file:
            

        if args.inputargprint:
            yaml = YAML()
            with open(args.input_file, 'r') as f:
                data = yaml.load(f)
                print_keys(data)
    if args.changes_file:

    # Apply changes and output the result
        apply_changes_and_output(args.input_file, args.changes_file, args.output)

if __name__ == '__main__':
    main()
