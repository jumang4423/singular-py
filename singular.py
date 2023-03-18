import argparse
import openai
import os
import json
import asyncio
import subprocess
import sys
from typing import Optional

OUTPUTS_STR = ""
TMP_FILE_PATH = "./tmp/tmp.py"

async def read_stream(stream, callback):
    global OUTPUTS_STR
    while True:
        try:
            line = await stream.readline()
            if not line:
                break
            decoded_line = line.decode()
            OUTPUTS_STR += decoded_line
            callback(decoded_line)
        except ConnectionResetError:
            # Connection lost, stop the task
            break


async def write_stream(stream):
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            stream.write(line.encode())
            await stream.drain()
        except ConnectionResetError:
            # Connection lost, stop the task
            break

def is_project_generated(project_name: str) -> bool:
    generated_file = os.path.join("build", f"{name}_generated.py")
    return os.path.isfile(generated_file)

def gen_singular(main_py_impl_file_path: str, func_list_json_file_path: str, gen_py_path: str, error_str: Optional[str] = None):
    print("@@@@@ given ERROR_STR: ", error_str if error_str else "None")
    print("@@@@@ given FUNC_LIST_JSON_FILE_PATH: ", func_list_json_file_path)
    print("@@@@@ given GEN_PY_PATH: ", gen_py_path)
    print("@@@@@ given MAIN_PY_IMPL_FILE_PATH: ", main_py_impl_file_path)
    main_py_str = ""
    with open(main_py_impl_file_path, "r") as f:
        main_py_str = f.read()

    func_list = []
    with open(func_list_json_file_path, "r") as f:
        func_list = json.load(f)

    abst_func_list = []
    for func in func_list:
        new_abst_func = {}
        new_abst_func["name"] = func["name"]
        new_abst_func["description"] = func["description"]
        new_abst_func["examples"] = []
        for example in func["examples"]:
            new_example_str = f"({', '.join(str(example['args']))}) returns {str(example['expected'])}"
            new_abst_func["examples"].append(new_example_str)

        abst_func_list.append(new_abst_func)
    abst_func_list_str = json.dumps(abst_func_list)

    SYSTEM_PROMPT = f"""
You are a very smart debugger AI. Your task is to generate or debug Python functions that work with the given main Python code.
You will not return any code that does not compile.

Main Python code:
{main_py_str}
    """

    USER_PROMPT = f"""
Functions JSON array:
```
{abst_func_list_str}
```
AI generated functions in Python (if any):
```
{error_str if error_str else "Not generated yet, please generate it"}
```
Error messages from terminal (if any):
```
{error_str if error_str else "There is no error"}
```
Based on the above information, please generate code based on functions JSON array, or debug ai generated functions in python that work with the given main Python code.
You only have to return the AI-generated function body in python, not the whole function.
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    new_functions_python_str = completion.choices[0].message.content
    # if build folder does not exist, create it
    if not os.path.isdir("build"):
        os.mkdir("build")
    with open(gen_py_path, "w") as f:
        f.write(new_functions_python_str)

async def start_debugger(main_py_impl_file_path: str, gen_py_path: str, func_list_json_file_path: str):
    # combine these files into ./tmp/tmp.py
    tmp_str = ""
    with open(gen_py_path, "r") as f:
        tmp_str += f.read()
    with open(main_py_impl_file_path, "r") as f:
        tmp_str += f.read()
    # if tmp folder does not exist, create it
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
    with open(TMP_FILE_PATH, "w") as f:
        f.write(tmp_str)
    global OUTPUTS_STR
    OUTPUTS_STR = ""

    if "process" in globals() and not process.returncode:
        process.kill()

    process = await asyncio.create_subprocess_exec(
        "python",
        TMP_FILE_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Track user input and program output
    asyncio.create_task(read_stream(process.stdout, sys.stdout.write))
    asyncio.create_task(read_stream(process.stderr, sys.stderr.write))
    asyncio.create_task(write_stream(process.stdin))

    await process.wait()

    if process.returncode != 0:
        print("\n\n ! error occurs, start re-generating new functions")
        print(OUTPUTS_STR)
        gen_singular(main_py_impl_file_path, func_list_json_file_path, gen_py_path, error_str=OUTPUTS_STR)
        print("ai debug finished. exit")
        # TODO: ugliest system, need to fix


# parse args
parser = argparse.ArgumentParser(description='auto test specific functions then fix based on python behavior, based on given python impl and function list json.')
parser.add_argument('--name', help='name of this project')
parser.add_argument('--app', help='path to the main Python program')
parser.add_argument('--fun', help='path to the function list JSON file')
try:
    args = parser.parse_args()
    name = args.name
    app = args.app
    fun = args.fun
    print(f"- project name: {name}")
except argparse.ArgumentError as e:
    print(f"Error: Invalid argument - {e}")
    parser.print_help()
except Exception as e:
    print(f"Error: {e}")

# Check if generated file exists
if not is_project_generated(name):
    print("no cached generated file found, generating...")
    gen_singular(app, fun, os.path.join("build", f"{name}_generated.py"))

print("start debugging...")
# TODO: need to impl continuous debugging right?
asyncio.run(start_debugger(app, os.path.join("build", f"{name}_generated.py"), fun))
