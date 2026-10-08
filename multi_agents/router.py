# Reference: 
"""
https://docs.langchain.com/oss/python/langgraph/workflows-agents#workflows-and-agents

Routing
Routing workflows process inputs and then directs them
to context-specific tasks. 
This allows you to define specialized flows for 
complex tasks. 
For example, a workflow built to answer product 
related questions might process the type of question 
first, and then route the request to specific processes for pricing, refunds, returns, etc.


"""

import getpass
import os
from tkinter import Image
from IPython.display import display
from IPython import display
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph, add_messages
from openai import OpenAI

load_dotenv()

print("Loading environment variables...")
try:
    api_key = os.getenv("OPENAI_API_KEY")
    #api_key = os.getenv("OPENAI_PERSONAL_KEY")
    #print(f"OPENAI_API_KEY: {api_key}")
    if not api_key:        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
except Exception as e:
    print(f"Error loading environment variables: {e}")
    print("Please ensure you have a .env file with the correct OPENAI_API_KEY.")    
    exit(1)
print("OPENAI_API_KEY loaded successfully.")
# Chat Model

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini", #gpt-4o
    # stream_usage=True,
    temperature=0.2,
)


#test_msg = llm.invoke("What is LLM? Write a short explanation with in 100 words.") #stream or invoke

#test_msg.content

# Print in Readable Format
#
# print(test_msg.content)

from pydantic import BaseModel, Field
#from typing_extensions import Literal
from typing import TypedDict,Literal
from langchain.messages import HumanMessage,SystemMessage

# Schema for structured output to use as routing logic
class Route(BaseModel):
    step: Literal["poem", "story", "joke"] = Field(None, description="The next step in the routing process"
    )
# Augment the LLM with schema for structured output
router = llm.with_structured_output(Route)

# State
class State(TypedDict):
    input: str
    decision: str
    output: str

# Nodes
def write_story(state: State):
    """Write a story"""

    result = llm.invoke(state["input"])
    return {"output": result.content}

def write_poem(state: State):
    """Write a poem"""
    result = llm.invoke(state["input"])
    return {"output": result.content}

def write_joke(state: State):
    """Write a joke"""
    result = llm.invoke(state["input"])
    return {"output": result.content}

def llm_call_router(state: State):
    """Route the input to the appropriate node"""
    
    # Run the augmented LLM with structured output to serve as routing logic

    decision = router.invoke(
        [SystemMessage(
                content="Route the input to story, joke, or poem based on the user's request."
            ),
            HumanMessage(content=state["input"])
        ]
    )
    return {"decision": decision.step}

# Conditional edge function to route to the appropriate node
def route_decision(state: State):
    # Return the node name you want to visit next
    # It can select only one node based on the below logic
    if state["decision"] == "story":
        return "write_story"
    elif state["decision"] == "joke":
        return "write_joke"
    elif state["decision"] == "poem":
        return "write_poem"

# Build workflow
router_builder = StateGraph(State)

# Add nodes
router_builder.add_node("write_story", write_story)
router_builder.add_node("write_joke", write_joke)
router_builder.add_node("write_poem", write_poem)
router_builder.add_node("llm_call_router", llm_call_router)

# Add edges to connect nodes
router_builder.add_edge(START, "llm_call_router")
router_builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {  # Name returned by route_decision : Name of next node to visit
        "write_story": "write_story",
        "write_joke": "write_joke",
        "write_poem": "write_poem",
    },
)
router_builder.add_edge("write_story", END)
router_builder.add_edge("write_joke", END)
router_builder.add_edge("write_poem", END)

# Compile workflow
router_workflow = router_builder.compile()

# Show the workflow
#display(Image(router_workflow.get_graph().draw_mermaid_png()))

# Invoke
state = router_workflow.invoke({"input": "Write me a joke about cats"}) #It will work

#The second half o the question is not working because the router is designed to route to only one node based on the decision made by the LLM. In this case, it will route to either "write_story", "write_joke", or "write_poem" based on the input. If you want to handle multiple requests in one input, you would need to modify the routing logic to handle that case, or split the input into separate requests.

state = router_workflow.invoke({"input": "Write me a joke about cats and write some jokes about dogs."})
print(state["output"])
