from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os, json

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in .env file")

client=OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------
# Tool (can upgrade later)
# -----------------------------
def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"

def run_command(cmd: str):
    result = os.system(cmd)
    return result

available_tools={
    "get_weather":get_weather,
    "run_command": run_command
}
# -----------------------------
# System Prompt
# -----------------------------
SYSTEM_PROMPT = """
 You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

"""

messages=[]
messages.append({"role":"system","content":SYSTEM_PROMPT})
query=input("> ")
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
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from assistant.")
    parsed_response = json.loads(content)
    if parsed_response.get("step")=="plan":
        print("💡 ",parsed_response.get("content"))
        continue
    elif parsed_response.get("step")=="action":
        tool_name=parsed_response.get("function")
        tool_input=parsed_response.get("input")
        print(f"Calling tool: {tool_name} with input parameters {tool_input}")
        output=available_tools[tool_name](tool_input)
        messages.append({"role":"user","content":json.dumps({"step":"observe","output":output})})
        continue
    elif parsed_response.get("step")=="output":
        print(parsed_response.get("content"))
        break