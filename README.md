# PEP8 Formatter

To use the formatter run the file __main__.py with a path to a folder with your .py files
```sh
__main__.py  -f <path_to_folder>
```
If a folder isn't specified the formatter will use the test folder in this directory

Your folder will be copied to the outputs folder in this directory with a name outputX where X is a number that
increases each run to allow easier multiple runs without emptying the output folder or losing the contents every time

The code was unit tested using pytest, you can run the tests using
```sh
pytest -v test
```

Pytest results:
![whole site](resources/results.png)