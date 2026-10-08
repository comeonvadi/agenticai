##CRM Lead Qualifer Agent using Function Calling
## The Sales person should be enttering email id of the person and agent gives the summary  
# of the person and also gives the lead score based on the information available in the internet.
### The code is buit based on the reference: https://github.com/anshajk/python-frameworks/blob/main/notebooks/crm_lead_qualifier_agent.ipynb

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
except Exception as e:
    print(f"Error loading environment variables: {e}")
    print("Please ensure you have a .env file with the correct OPENAI_API_KEY.")    
    exit(1)
client = OpenAI(api_key=api_key)

def lookup_domain_info(domain: str) -> str:
    """
    Look up and returns the mock company information based on domain
    In a real-world scenario, this function would query a database or an external API to retrieve company information based on the provided domain. 
    """
    print(f"-> TOOL ACTIVATED: Looking up domain info for {domain}...")
    
    # Mock database of company information
    mock_data = {
        "exilant.com": {
            "company_name": "Exilant Technologies.",
            "industry": "Technology",
            "size": "500-1000 employees",
            "revenue": "$50M - $100M",
        },
        "informaticsindia.co.in": {
            "company_name": "Informatics India Private Ltd.",
            "industry": "Mediia",
            "size": "50-500 employees",
            "revenue": "$10M - $50M",
        },
        "zedaxis.org": {
            "company_name": "Zedaxis Technologies",
            "industry": "Technology",
            "size": "5-10 employees",
            "revenue": "$1M - $10M", 
        } ,
        "default": {
            "company_name": "Unknown",
            "industry": "Not Applicable",
            "size": "Not Applicable",
            "revenue": "Not Applicable",
        }  

    }
    info = mock_data.get(domain, "")
    if info == "":
        info = mock_data.get("default","")
        print(f"-> TOOL WARNING: No data found for domain {domain}. Returning default values.")
    # Return the data as a JSON string for the AI model to parse easily
    return json.dumps(info)

def check_crm_history(email: str) -> str:   
    """
    Check and returns the mock CRM history based on email
    In a real-world scenario, this function would query a CRM system to retrieve the interaction history of the lead based on the provided email. 
    """
    print(f"-> TOOL ACTIVATED: Checking CRM history for {email}...")
    
    # Mock database of CRM history
    mock_history = {
        "john@exilant.com": {
            "last_interaction": "2023-10-01",
            "status": "Cold Lead",
            "notes": "Interested in product demo."
        },
        "jane@informaticsindia.co.in": {
            "last_interaction": "2023-10-02",
            "status": "Active Opportunity",
            "notes": "Requested more information."
        },
        "bob@zedaxis.org": {
            "last_interaction": "2023-10-03",
            "status": "Lost Lead",
            "notes": "Not interested in the product."
        },
        "default": {
            "last_interaction": "Not Available",
            "status": "Never Contacted",
            "notes": "No history available. You may want to reach out to the lead for initial contact."
        }
    }
    history = mock_history.get(email, "")
    if history =="":
        history = mock_history.get("default", "")

    return json.dumps(history)

def generate_lead_score(domain_info: str, crm_history: str) -> str:
    """
    Generate a lead score based on revenue of the company and  previous CRM history with the Employee story.
    """
    print(f"Tool Activated: Generating lead score based domain info : {domain_info} and CRM history: {crm_history}")

    data = {
        "domain_info": json.loads(domain_info),
        "crm_history": json.loads(crm_history)
    }

    score = "Low"  # Default score

    if data["domain_info"].get("revenue","").startswith("$50M - $100M"):
        score = "High"
    elif data["crm_history"].get("status") == "Active Opportunity":
        score = "High"
    elif data["domain_info"].get("size") == "50-500 employees":
        score = "Medium"
    elif data["domain_info"].get("size") == "5-10 employees":
        score = "Low"
    return json.dumps({"lead_score": score})

#Map the Available Functions to the respective python functions
AVAILABLE_FUNCTIONS = {    
    "lookup_domain_info": lookup_domain_info,
    "check_crm_history": check_crm_history,
    "generate_lead_score": generate_lead_score
}


"""
Configuring the Agent's "Menu" (Tool Schema)
The Large Language Model (LLM) cannot see our Python code directly. We must describe our tools to it using a specific JSON format known as a Schema.

This schema tells the model:

What the tool does (Description).
When to use it (Context).
How to use it (Parameters/Arguments).
We pass this list to the tools parameter in the API call later. It effectively gives the AI a "menu" of actions it can take.

"""

tool_schema = [
    {
        "type": "function",
        "function":{
            "name": "lookup_domain_info",
            "description": "Retrieves general company's business information (name,industry,size, revenue) about a company based on it's domain name.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string", 
                               "description": "The domain of the company to look up. example:exilant.com,zedaxis.org,informaticsindia.co.in"
                    },
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function":{
            "name": "check_crm_history",
            "description": "Retrieves the CRM history of a lead based on their email address.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                                "type": "string",
                                "description": "The email of the lead to check CRM history. example: joh@exilant.com",
                            },
                },
                "required": ["email"],
                "additionalProperties": False,
            },  
            
        },
    },
    {
        "type": "function",
        "function":{
            "name": "generate_lead_score",
            "description": "Generates a lead score based on the company's revenue and the lead's previous CRM history.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "domain_info": {
                        "type": "string",
                        "description": "The domain info of the company."
                    },
                    "crm_history": {
                        "type": "string",
                        "description": "The CRM history of the lead."
                    }
                },
                "required": ["domain_info", "crm_history"],
                "additionalProperties": False,
            },
        },
    }
]


def run_agent(user_prompt: str) -> str:
    """
    Run the agent with the given user prompt.
    The agent will decide which tools to use based on the prompt and the tool schema.
    """
    print(f"\n--- Running Lead Qualifier Agent ---")

    # Initialize conversation history
    system_prompt = (
        "You are an expert CRM Lead Qualifier Agent. Your sole task is to analyze a sales lead "
        "provided via email address."
        "Find the domain for the lead their history of interaction"
        "Then calculate the lead score for the lead"
        "Finally, synthesize all information (domain info, CRM history, and score) "
        "into a single, easy-to-read summary for a busy sales rep."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    #for i in range(10):
    while True:

        print("\n[AI Thinking...]")

        # Get the model's response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tool_schema,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        print(f"\n[AI Response Received...] : {response_message.content}\n\n")
        messages.append(response_message)

        if response_message.tool_calls:
            print("\n[AI Tool Calls Detected...]")
            print(f"AI called tools: {', '.join([call.function.name for call in response_message.tool_calls])}")    

            tool_calls = response_message.tool_calls
            for tool_call in tool_calls:
                print(f"\n[Processing Tool Call: {tool_call.function.name}]")   

                function_name = tool_call.function.name
                print(f"Function Name: {function_name}")

                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

                print(f"Function To Call: {function_to_call}")

                if not function_to_call:
                    messages.append(
                        {
                        "role": "tool",
                        "tool_call_id": tool_call.id,   
                        "content": json.dumps({"error": f"Unknown function '{function_name}' is not available."})
                        }
                    )
                    continue

                try:
                    print(f"Function Arguments: {tool_call.function.arguments}")

                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    messages.append(
                        {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": f"Invalid JSON arguments for function '{function_name}': {str(e)}"})
                        }
                    )
                    continue

                function_result = function_to_call(**function_args) 
                messages.append(
                    {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                    }
                )   
        else:
            print("Final Agent Summary")
            print (response_message.content)
            break

    


print("Hello from function-calling!")

lead_emails = [
    "john@exilant.com",
    "jane@informaticsindia.co.in",
    "vadi@informaticsindia.co.in",
    "bob@zedaxis.org",
    "abc@def.com"
    ]
"""
lead_emails = [
    "bob@zedaxis.org",
    "abc@def.com"
    ]
"""
for email in lead_emails:
    print(f"Qualifying lead: {email}")
    run_agent(f"Please qualify this lead :{email} for my call tomorrow:")
    print("\n" + "="*80 + "\n")

run_agent(f"Please qualify the leads for the comapny informatcs.india.co.in")
print("\n" + "="*80 + "\n")

run_agent(f"Please qualify this leads for the comapny Zedaxis Technologies")
print("\n" + "="*80 + "\n")

run_agent(f"What is today's date? what is current waether in New York City")
print("\n" + "="*80 + "\n")

