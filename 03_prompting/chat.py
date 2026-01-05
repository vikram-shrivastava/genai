import json
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)
SYSTEM_PROMPT="""
    You are and helpful AI assistant which is specialized in resolving user queries.
    For the given user input, analyse the input and breakdown the problem in step by step.
    
    The Steps are you get the user input, you analyze the input then you think, you think again for several times till you get the correct output

    Follow the steps in sequence that is "analyze", "think", "output", "validate" and finally "result"

    Rules:
    1. Always respond with a JSON object containing the step and content.
    2. Always perform one step at a time.
    3. Carefully analyze the user query.

    Output Format:
    {{""}}
    Example:
    Input: What is 2+2
    Output: {{"step":"analyze","content":"Alright! user is interested in maths query and he is looking for addition operation between two number 2 and 2."}}
    Output: {{"step":"think","content":"Let me calculate the sum of 2 and 2, which can be done by addition operation between those two number (2+2)"}}
    Output: {{"step":"think","content":"The output of the operation of addition on two operand 2 and 2 will be 2+2=4"}}
    Output: {{"step":"result","content":"The sum of 2 and 2 is 4. As, 2 + 2 = 4"}}

"""
messages=[]
messages.append({"role":"system","content":SYSTEM_PROMPT})
query=input("->")
messages.append({"role":"user","content":query})
while True:
    response=client.chat.completions.create(
        model='gpt-4.1-mini',
        response_format={"type":"json_object"},
        messages=messages,
        max_tokens=2000,
        temperature=0.5
    )
    messages.append({"role":"assistant","content":response.choices[0].message.content})
    if response.choices[0].message.content is not None:
        parsed_response = json.loads(response.choices[0].message.content)
    else:
        parsed_response = {}
    if parsed_response.get("step") != "result":
        print("🧠:",parsed_response.get("content"))
    print("🤖:",parsed_response.get("content"))
    break