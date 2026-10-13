# afsar code examples
To bootstrap Python students I want to have the following example

Examples should be self contained single file scripts.
They should reside in an `examples` directory.

## teach_literals
This example - when you run it test if the students know how to write different literals in python including int, floats, binaries, string of all kind of quotes, single line and multi lines.

The flow of the example includes two LLM calls.
Call 1 - use high temperature and ask the LLM to create a question about literals.
script displays the question and asks for user input
Call 2 - calling the LLM with the original question, request to test it and a template of a python script that runs the users code inside the script - e.g. 
```
value = {repr(user_answer)}
print(value)
```

The prompt for Call 2 may also request to explain the errors of the student if any.

## inspect_literals
This example uses afsar to run `examples/teach_literals.py` 5 times (providing sample student answers), inspects the source code, and reports on whether the program does a good job covering the topic 'literals' and whether it has any bugs, issues, or pedagogical limitations.
