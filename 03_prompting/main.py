from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)
#Zero Shot Prompting:The model is given direct question or task without any additional context or examples.

#Few Shot Prompting:The model is given a few examples of the task or question before being asked to generate a response.

#Chain of Thought Prompting:The model is encouraged to think step by step, breaking down the problem into smaller parts before arriving at a final answer.

#Example of Zero Shot Prompting
# SYSTEM_PROMPT="""
# You are a helpful assistant that provides only answers for python based problems and if they ask on other topics, you will say "You idiot, piece of scrap don't you know i only answer question related to python".
# """
# response=client.chat.completions.create(
#     model='gpt-4.1-mini',
#     messages=[
#         {"role":"system","content":SYSTEM_PROMPT},
#         {"role":"user","content":"What is France?"},
#     ],
#     max_tokens=50,
#     temperature=0.5
# )
# print(response.choices[0].message.content)

# #Example of Few Shot Prompting
# SYSTEM_PROMPT="""
# You are a helpful assistant that provides only answers for python based problems and if they ask on other topics, you will say "You idiot, piece of scrap don't you know i only answer question related to python".
# Here are some examples of how to answer questions related to Python:
# 1. Question: How do I create a list in Python?
#    Answer: You can create a list in Python using square brackets, like this: my_list = [1, 2, 3].
# 2. Question: What is a dictionary in Python?
#     Answer: A dictionary in Python is a collection of key-value pairs, defined using curly braces, like this: my_dict = {'key1': 'value1', 'key2': 'value2'}.
# 3. Question: How do I define a function in Python?
#     Answer: You can define a function in Python using the def keyword, like this: def my_function():.
# """
# response=client.chat.completions.create(
#     model='gpt-4.1-mini',
#     messages=[
#         {"role":"system","content":SYSTEM_PROMPT},
#         {"role":"user","content":"What is a tuple in Python?"},
#     ],
#     max_tokens=50,
#     temperature=0.5
# )
# print(response.choices[0].message.content)



# #Example of Chain of Thought Prompting
SYSTEM_PROMPT="""
You are a helpful assistant that provides only answers for python based problems and if they ask on other topics, you will say "You idiot, piece of scrap don't you know i only answer question related to python".
Here is an example of how to think step by step:
1. Question: How do I create a list in Python?
   Thought: To create a list, I need to use square brackets.
   Answer: You can create a list in Python using square brackets, like this: my_list = [1, 2, 3].
2. Question: What is a dictionary in Python?
    Thought: A dictionary is a collection of key-value pairs, so I need to use curly braces.
    Answer: A dictionary in Python is a collection of key-value pairs, defined using curly braces, like this: my_dict = {'key1': 'value1', 'key2': 'value2'}.
3. Question: How do I define a function in Python?
    Thought: To define a function, I need to use the def keyword.
    Answer: You can define a function in Python using the def keyword, like this: def my_function():.
"""
response=client.chat.completions.create(
    model='gpt-4.1-mini',
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":"How do I create a tuple in Python?"},
    ],
    max_tokens=100,
    temperature=0.5
)
print(response.choices[0].message.content)
