from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
# use the openai module (reads OPENAI_API_KEY from env via load_dotenv)
client = OpenAI()

class State(TypedDict):
    query:str
    llm_result:str

def chatBot(state:State): #this is a node in langgraph
    #call openai with this query
    query=state["query"]
    llmresponse = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"user","content":query}
        ]
    )
    result=llmresponse.choices[0].message.content
    state['llm_result']=result
    return state

graph_builder=StateGraph(State)
graph_builder.add_node("chatBot",chatBot)
graph_builder.add_edge(START,"chatBot")
graph_builder.add_edge("chatBot",END)

graph=graph_builder.compile()

def main():
    user=input('>')
    #invoke the graph
    _state:State={
        "query":user,
        "llm_result":""
    }
    graph_result=graph.invoke(_state)
    print("Graph Result:",graph_result)

main()