##The Autonomous IT Support Agent using Function Calling
## ObjectYou are building an AI agent that acts as the "first responder" for server incidents. It must:
##Investigate: Check server health and logs when a user reports an issue.
##Act: If CPU is critical (>90%), it should Restart the service.
##Escalate: If the issue is complex or logs show "Payment Gateway Error", it should Escalate to a human.

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

# --- Already implement tool 1: Check Health ---
def get_server_health(server_id: str) -> str:
    """Returns CPU and Memory usage for a given server."""
    print(f"-> TOOL: Checking health for {server_id}...")

    metrics = {
        # Scenario 1: High CPU (Needs Restart)
        "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},

        # Scenario 2: Healthy (No Action Needed)
        "db-node-02": {"cpu": "12%", "memory": "60%", "status": "Healthy"},

        # Scenario 3: High Memory Leak (Needs Restart or Escalation)
        "auth-service-03": {"cpu": "45%", "memory": "95%", "status": "Critical"},

        # Scenario 4: Network/Dependency Failure (Needs Escalation)
        "search-index-09": {"cpu": "10%", "memory": "15%", "status": "Error"},

        # Scenario 5: Completely Normal
        "frontend-node-04": {"cpu": "25%", "memory": "30%", "status": "Healthy"},
    }

    result = metrics.get(server_id, {"error": "Server not found. Check the ID."})
    return json.dumps(result)


def fetch_recent_logs(server_id: str, lines: int = 5) -> str:
    """Returns the last N lines of logs."""
    print(f"-> TOOL: Fetching last {lines} log lines for {server_id}...")

    # Different logs for different servers to trigger different agent behaviors
    log_database = {
        "payment-server-01": [
            "[INFO] Request received /pay/v1",
            "[WARN] CPU threshold exceeded 90%",
            "[WARN] Thread pool exhaustion",
            "[CRITICAL] Process hung, not accepting new connections",
            "[ERROR] Timeout waiting for thread"
        ],
        "db-node-02": [
            "[INFO] Backup started",
            "[INFO] Backup completed successfully",
            "[INFO] User query executed in 12ms",
            "[INFO] Health check: OK",
            "[INFO] Replication sync active"
        ],
        "auth-service-03": [
            "[INFO] Token validated user_882",
            "[WARN] Garbage collection taking too long (>5s)",
            "[ERROR] java.lang.OutOfMemoryError: Java heap space",
            "[CRITICAL] Application crashing due to memory leak",
            "[INFO] Restarting context..."
        ],
        "search-index-09": [
            "[INFO] Indexing started",
            "[ERROR] Connection refused: elastic-cluster-main:9200",
            "[ERROR] Failed to write document ID 4432",
            "[CRITICAL] Dependency Unreachable: Search Engine is down",
            "[ERROR] Retrying in 30s..."
        ],
        "frontend-node-04": [
            "[INFO] GET /home 200 OK",
            "[INFO] GET /assets/logo.png 200 OK",
            "[INFO] GET /login 200 OK",
            "[INFO] GET /api/v1/status 200 OK",
            "[INFO] Health check passed"
        ]
    }

    # Default logs if server not found in specific list
    default_logs = ["[INFO] System stable", "[INFO] Heartbeat signal received"]

    logs = log_database.get(server_id, default_logs)
    return json.dumps({"logs": logs[:lines]})

def restart_service(server_id: str) -> str:
    """Simulates a service restart."""
    print(f"-> TOOL: Restarting service {server_id}...")

    # In a real scenario, this would run a subprocess command or API call
    result = {
        "server_id": server_id,
        "status": "success",
        "message": "Service restart command issued successfully."
    }
    return json.dumps(result)
def escalate_to_engineer(summary: str) -> str:
    """Simulates sending an alert to a human."""
    print(f"-> TOOL: Escalating to human engineer. Reason: {summary}")

    # In a real scenario, this would send a Slack message or PagerDuty alert
    result = {
        "status": "escalated",
        "ticket_id": "INC-999",
        "assigned_to": "On-Call Engineer",
        "summary_of_issue": summary
    }
    return json.dumps(result)



# Map functions for the agent execution loop
AVAILABLE_FUNCTIONS = {
    "get_server_health": get_server_health,
    "fetch_recent_logs": fetch_recent_logs,
    "restart_service": restart_service,
    "escalate_to_engineer": escalate_to_engineer,
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

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_server_health",
            "description": "Checks the current CPU and memory usage of a specific server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server, e.g., 'payment-server-01'"}
                },
                "required": ["server_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_recent_logs",
            "description": "Retrieves the most recent log entries from a server to diagnose errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server."},
                    "lines": {"type": "integer", "description": "Number of log lines to fetch."}
                },
                "required": ["server_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": "Restarts a specific server service. Use this when CPU usage is critically high or the process is unresponsive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server to restart."}
                },
                "required": ["server_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "escalate_to_engineer",
            "description": "Escalates the issue to a human engineer.Use this when automated fixes fail, or when the error logs indicate a complex issue like a payment gateway failure.",
            "parameters": {
                "type": "object",
                "properties": {
                     "summary": {"type": "string", "description": "A brief summary of the findings (health status, log errors) and why you are escalating."}
                },
                "required": ["summary"]
            }
        }
    }
]


def run_it_agent(user_issue: str):
    print(f"\n--- New Incident: {user_issue} ---")

    messages = [
        {"role": "system", "content": "You are a Level 1 IT Responder. Investigate server issues. "
                                      "If CPU or Memory is > 90%, restart the service. If logs show critical dependency errors (like connection refused) that a restart won't fix, escalate to an engineer."},
        {"role": "user", "content": user_issue}
    ]

    while True:
        print("\n[AI Thinking...]")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message
        messages.append(response_msg)

        print("Response message: ", response_msg)

        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

#                print(f"LLM asked us to call the function {func_name} with these arguments {func_args}")
                # Retrieve the actual python function based on name
                function_to_call = AVAILABLE_FUNCTIONS.get(func_name)

                if function_to_call:
                    # Execute the function
                    tool_output = function_to_call(**func_args)

                    # --- SOLUTION TASK 5: Append the result to messages ---
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,  # CRITICAL: Links output to the request
                        "name": func_name,
                        "content": tool_output
                    })

        else:
            print(f"\n[FINAL RESPONSE]: {response_msg.content}")
            break

    


print("Hello from function-calling!")

scenarios = [
    "The payment-server-01 is extremely slow and timing out.",
    "Something is wrong with db-node-02",
    "Users are reporting login failures on auth-service-03.",
    "Search isn't working. Can you check search-index-09?",
    "Check frontend-node-04 just to be safe."
    ]


for scenario in scenarios:
    print(f"Running Agent for the: {scenario}")
    run_it_agent(f"{scenario}")
    print("\n" + "="*80 + "\n")

