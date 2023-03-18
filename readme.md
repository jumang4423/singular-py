# singular-py

attension: gpt4 is required.

auto test specific functions then fix based on python behavior, based on given python impl and function list json.

# usage
0. export your OPEN_AI_KEY to shell environment.

``` bash
export OPENAI_API_KEY='sk-...'
```

1. specify two files to singular.py.

- function list json file
  function list to automatically to be managed by ai.

- main python program
  you write python program, but you can use functions in the function list.
 
here is a example:
``` bash
python singular.py --name add_test --app examples/add.py --fun examples/add.json
```

2. intract with your python app on singular.py 

just intract with your python app so that ai can detect errors.
if error occured, singular.py automatically re-generate functions.

3. finish debbuging
once you satisfied with your python app behavior, exit singular.py by ctrl-c then goto ./build folder now you can find auto generated functions. 

