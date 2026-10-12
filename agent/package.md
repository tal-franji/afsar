# afsar - simpke students' API to LLMs
This is a package installable from pypi

We want a package with API that can call:
* local agent's models - e.g. if claude-code installed - use the selected model (sonnet etc.) if codex or antigravity install - use the relevant models. This allows students who already have agents installed use the same models to write programs using these LLMs.
* remote API (e.g. OpenAI, Gemini etc.) - if given API_KEY via envrionment variables or function calls - allow using the same API

## API functionality
Allow calling the default/configured LLM with a prompt, allow to enable/disable thoughts, allow to control format text/json, allow usage of default tools (e.g. running local python programs, accessing files etc.)
The API is procedural (rather than OOP) to allow beginers to understand it easily.

## API
```python
import afsar

afsar.setup()
answer = afsar.ask("How do you define a function in Python?")
print(answer)
```
### afsar.setup
Setup is explicit. No auto setup happens in import and no auto setup is called on the first `ask` call. This makes things very explicit for beginners.
no required arguments - default finds the correct model and uses it.
has optional override parameter of model, API_KEY etc.

functionality - auto-detection order (e.g., check local   
  claude-code → check antigravity → check GEMINI_API_KEY → OPENAI_API_KEY)

tools usage - by default `tools=["python", "files"]` 
This default will not work for remote models so user must explicitly give `tools=[]` 
when working with remote models.

### afsar.ask()
required parameter - prompt
optional parameters: 
format="text"  # text is default "json" allowed, no schema. retuned type is always `str`
schema=class  # models that support Pydantic models. if given - `format` is ignored.
temperature
thinking=None # allowed None/True/False - if given True and the model used does not support thinking - raise ValueError exception

and maybe others

### afsar.ask_full()
Future
if we require to get a complex result object with thoughts, tools etc. - we will add `ask_full`