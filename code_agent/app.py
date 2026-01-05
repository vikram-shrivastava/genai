# corrected_assistant_v2.py
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import os
import json
import re
from typing import Optional, List, Dict

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in .env file")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

# -----------------------------
# Safety: basic blacklist for obviously destructive shell commands.
# You can expand this as needed.
DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\b:\s*(){\s*:;\s*};\s*\b",  # fork bomb partial
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bpoweroff\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r"\b:(){:|:&};:\b"
]

def is_safe_command(cmd: str) -> bool:
    low = cmd.lower()
    for p in DANGEROUS_PATTERNS:
        if re.search(p, low):
            return False
    # don't run interactive sudo by default
    if "sudo" in low:
        return False
    return True

def run_command(cmd: str) -> str:
    """
    Executes `cmd` in a subprocess and returns combined stdout/stderr and returncode.
    It refuses to run obviously dangerous commands (simple blacklist).
    """
    if not cmd or not cmd.strip():
        return "Empty command - nothing to run."

    if not is_safe_command(cmd):
        return f"Refused to run unsafe command: {cmd}"

    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        out = completed.stdout or ""
        err = completed.stderr or ""
        code = completed.returncode
        return f"returncode: {code}\nSTDOUT:\n{out}\nSTDERR:\n{err}"
    except Exception as e:
        return f"Exception when running command: {e}"

available_tools = {"run_command": run_command}

# -----------------------------
SYSTEM_PROMPT = """
You are an AI Assistant specialized in generating, debugging, and optimizing React.js and Next.js code.
For the given user query and available tools, plan the step by step execution, based on the planning,
Select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
Working mode: start -> plan -> action -> observe -> end.
Wait for the observation and based on the observation from the tool call resolve the user query.
   
Rules (strict):
- ALWAYS output exactly one valid JSON object and nothing else (no markdown, no extra commentary).
 - Follow the Output JSON Format.
- Always perform one step at a time and wait for next input
- Carefully analyse the user query
- The JSON must follow this schema:

Output JSON Format:
{{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function",
}}
Available Tools:
- "run_command": Takes linux command as a string and executes the command and returns the output after executing it.
Example:
    User Query: Create a simple Next.js app with a homepage that says Hello World. and folder name is myapp
    Output: {{ "step": "plan", "content": "The user is interested in creating a Next.js app with a homepage that says Hello World" }}
    Output: {{ "step": "plan", "content": "I should first create a folder where i need to create the project." }}
    Output: {{ "step": "plan", "content": "From the available tool i should call run_command tool to create a folder using linux command" }}
    Output: {{ "step": "action", "function": "run_command", "input": "mkdir homepage" }}
    Output: {{ "step": "observe", "output": "The folder should be present in current working directory" }}
    Output: {{ "step": "plan", "content": "Now I should create a next.js app using npx create-next-app@latest command" }}
    Output: {{ "step": "action", "function": "run_command", "input": "npx create-next-app@latest myapp --use-npm --app --eslint --src-dir --import-alias @/* --tailwind" }},d-,d
    Output: {{ "step": "observe", "output": "The next.js app should be created in myapp folder" }}
    Output: {{ "step": "plan", "content": "Now I should modify the index.js file to update the homepage to say Hello World" }}
    Output: {{ "step": "action", "function": "run_command", "input": "echo 'export default function Home()  return <h1>Hello World</h1> ' > myapp/src/app/page.js" 
    }}
    Output: {{ "step": "observe", "output": "The index.js file should be updated" }}
    Output: {{ "step": "plan", "content": "Now I should run the next.js app using npm run dev command" }}
    Output: {{ "step": "action", "function": "run_command", "input": "cd myapp && npm run dev" }}
    Output: {{ "step": "observe", "output": "The next.js app should be running on localhost:3000" }}
    Output: {{ "step": "output", "content": "The application should be running at localhost:3000" }}

- If you want the system to execute a shell command, set "function": "run_command" and put the shell command string in "input".
- After a function call is executed, the system will append an observation (tool output) and call you again so you can continue the flow.
- If a user request is NOT about React/Next.js code generation, reply exactly with:
  "I'm Tony Stark. I'm not here to discuss that. Let's stick to topics I care about—tech, Marvel, my family, or my personal life. Anything else is just not worth my time."
"""

# -----------------------------
messages = []
messages.append({"role": "system", "content": SYSTEM_PROMPT})
query = input("> ")
messages.append({"role": "user", "content": query})
while True:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    msg = response.choices[0].message.content
    print(msg)
    if msg is not None:
        try:
            js = json.loads(msg)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print("Please ensure the output is a valid JSON object.")
            break

        if js.get("step") == "action":
            func_name = js.get("function")
            func_input = js.get("input")
            if func_name in available_tools:
                func = available_tools[func_name]
                output = func(func_input)
                messages.append({"role": "assistant", "content": msg})
                messages.append({"role": "user", "content": f'{{ "step": "observe", "output": "{output}" }}'})
            else:
                print(f"Function {func_name} not found in available tools.")
                break
        elif js.get("step") == "output":
            print("Final Output:", js.get("content"))
            break
        else:
            messages.append({"role": "assistant", "content": msg})