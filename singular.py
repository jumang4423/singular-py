import argparse
import os

# parse args
parser = argparse.ArgumentParser(description='auto test specific functions then fix based on python behavior, based on given python impl and function list json.')
parser.add_argument('--name', help='name of the function to run')
parser.add_argument('--app', help='path to the main Python program')
parser.add_argument('--fun', help='path to the function list JSON file')
try:
    args = parser.parse_args()
    name = args.name
    app = args.app
    fun = args.fun
    print(f"Function name: {name}")
    print(f"Main Python program path: {app}")
    print(f"Function list JSON file path: {fun}")
except argparse.ArgumentError as e:
    print(f"Error: Invalid argument - {e}")
    parser.print_help()
except Exception as e:
    print(f"Error: {e}")

# Check if generated file exists
generated_file = os.path.join("build", f"{name}_generated.py")
if os.path.isfile(generated_file):
    print(f"Generated file exists: {generated_file}")
else:
    print("no cached generated file found, generating...")
