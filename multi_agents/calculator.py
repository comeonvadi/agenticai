#Reference : https://docs.langchain.com/oss/python/langgraph/quickstart
#Install langgraph and langchain
#Install langchain-openai

import os
import getpass
from xml.parsers.expat import model
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI

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

# Define tools and Models



# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b
@tool
def sub(a: int, b: int) -> float:
    """Subtract `b` from `a`.

    Args:
        a: First int
        b: Second int
    """
    return a - b

#Define Model
model = ChatOpenAI(
    model="gpt-4o-mini", #gpt-4o
    # stream_usage=True,
    temperature=0) #to provide accurate results, we set temperature to 0. If you want more creative results, you can increase the temperature value.


# Augment the LLM with tools
#print(type(add))
tools = [add, multiply, divide, sub]
tools_by_name = {tool.name: tool for tool in tools}
#print(type(tools_by_name))
#print(tools_by_name)
model_with_tools = model.bind_tools(tools)

#Define State
"""
State in LangGraph persists throughout the agent’s execution.
The Annotated type with operator.add ensures that new messages are 
appended to the existing list rather than replacing it.

The graph’s state is used to store the messages and the number of LLM calls.

"""

from langchain.messages import AnyMessage
from typing_extensions import Annotated,TypedDict
import operator
class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add] = []
    llm_calls: int


#Define Model Node
# The model node is used to call the LLM and decide whether to call a tool or not.

from langchain.messages import SystemMessage

def llm_call(state:dict):
    """LLM decides where to call tool or not"""
    return {
        "messages":[
            model_with_tools.invoke(
                [SystemMessage(content="You are a helpful assistant that can perform mathematical operations. You have access to the following tools: add, multiply, divide, sub. Use these tools to perform calculations when necessary."
                               )
        ]
        + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

#define Tool Node
#The tool node is used to call the tools and return the results.

from langchain.messages import ToolMessage

def tool_node(state:dict):
    """Tool Node. Performs the tool call based on the last message in the state."""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool=tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

#Define end logic
#The conditional edge function is used to route to the tool node or end 
# based upon whether the LLM made a tool call.
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
    #if getattr(last_message, "tool_calls", None):

        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END


#6. Build and compile the agent
#The agent is built using the StateGraph class and compiled using the compile method.

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# Show the agent
from IPython.display import Image, display
display(Image(agent.get_graph(xray=True).draw_mermaid_png()))

# Invoke
from langchain.messages import HumanMessage
messages = [HumanMessage(content="Add 3 and 4.Tell me the joke about cats. Then multiply 5 and 6. Then divide 10 by 2. Then subtract 2 from 5.")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()

