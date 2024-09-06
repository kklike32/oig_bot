import sys
import os
import oci
import requests
import json

# Load OCI Config and Generative AI Client
compartment_id = "SAMPLE"
CONFIG_PROFILE = "DEFAULT"  # Adjust this to your OCI config profile
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
    config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240)
)

# Function to get LLM response from Oracle GenAI
def get_llm_response(user_query: str) -> str:
    tool_prompt = f"""
    I have the following tools that I can use to fetch information from Oracle Identity Manager:
    
**Get Users** (get_users): Fetches all users in Oracle Identity Manager, optionally filtered by a criterion. Parameters:
`fields`: Specifies which user attributes to return.
`q`: Filter criteria, e.g., 'Last::Name sw G' to get users whose last name starts with 'G'.
    
**Get Roles** (get_roles): Fetches all roles in Oracle Identity Manager, optionally filtered by a criterion. Parameters:
`fields`: Specifies which role attributes to return.
`q`: Filter criteria, e.g., 'Role::Name sw Oracle' to get roles whose name starts with 'Oracle'.
    
**Get Policies** (get_policies): Fetches all policies in Oracle Identity Manager, optionally filtered by type or role ID. Parameters:
`policyType`: Specifies the type of policy (accessPolicy, passwordPolicy, etc.).
`q`: Additional filter criteria, e.g., 'name sw A' for policies starting with 'A'.
`roleId`: Filters by role ID, e.g., '1234'.
    
    Based on the user's question, choose the most relevant tool and return the tool name and the appropriate parameters as a string, if the question is bsaic, there is no need to fill out the parameters, leave it blank, like:
    tool_name: <tool_name>, parameters: {{'q': 'Role::Name sw Oracle'}}
    
    User Query: "{user_query}"
    """
    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = tool_prompt
    chat_request.max_tokens = 600
    chat_request.temperature = 1
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
        model_id="MODEL ID"
    )
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response_text = chat_response.data.chat_response.text
    print(f"This is the response text: {response_text}\n\n\n")
    return response_text

# Define the tools (API endpoints)
tools = [
    {
        "name": "get_users",
        "description": "Returns all the users in Oracle Identity Manager, optionally filtered by a criterion.",
        "parameter_definitions": {
            "fields": {
                "description": "Specifies which user attributes to return.",
                "type": "str",
                "required": False
            },
            "q": {
                "description": "Filter criteria, e.g., 'Last::Name sw G' to get users whose last name starts with 'G'.",
                "type": "str",
                "required": False
            }
        }
    },
    {
        "name": "get_roles",
        "description": "Fetches all the roles in Oracle Identity Manager, optionally filtered by a criterion.",
        "parameter_definitions": {
            "fields": {
                "description": "Specifies which role attributes to return.",
                "type": "str",
                "required": False
            },
            "q": {
                "description": "Filter criteria, e.g., 'Role::Name sw Oracle' to get roles whose name starts with 'Oracle'.",
                "type": "str",
                "required": False
            }
        }
    },
    {
        "name": "get_policies",
        "description": "Fetches all policies in Oracle Identity Manager, optionally filtered by type or role ID.",
        "parameter_definitions": {
            "policyType": {
                "description": "Specifies the type of policy (accessPolicy, passwordPolicy, etc.).",
                "type": "str",
                "required": True
            },
            "q": {
                "description": "Additional filter criteria, e.g., 'name sw A' for policies starting with 'A'.",
                "type": "str",
                "required": False
            },
            "roleId": {
                "description": "Filters by role ID, e.g., '1234'.",
                "type": "str",
                "required": False
            }
        }
    }
]

# Parse the string response from the LLM to extract tool_name and parameters
def parse_llm_response(llm_response: str):
    # Example format expected: "tool_name: get_roles, parameters: {'q': 'Role::Name sw Oracle'}"
    try:
        # Split by commas and colons to extract tool_name and parameters
        parts = llm_response.split(", ")
        tool_name_part = parts[0].split(": ")[1].strip()
        parameters_part = parts[1].split(": ")[1].strip()
        # Convert the parameters part to a dictionary using eval
        parameters = eval(parameters_part)  # Caution: Ensure the string is safe before using eval
        return tool_name_part, parameters
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        # Fallback to default tool_name and parameters if parsing fails
        return "get_users", {}

# Function to execute the selected API call based on the tool with authentication

def execute_tool_call(tool_name, parameters, username, password):

    base_url = "http://celvpvm02333.us.oracle.com:14000/iam/governance/selfservice/api/v1/"

    headers = {"Content-Type": "application/json"}

    auth = (username, password)
    
    # Handle 'get_users'tool
    if tool_name == "get_users": 
        url = base_url + "users" 
        if parameters.get("q"): 
            url += f"?q={parameters['q']}" 
        if parameters.get("fields"): 
            url += f"&fields={parameters['fields']}" 
        response = requests.get(url, headers=headers, auth=auth) 
        return response.json() 
    # Handle 'get_roles' tool 
    elif tool_name == "get_roles": 
        url = base_url + "roles" 
        if parameters.get("q"): 
            url += f"?q={parameters['q']}" 
        if parameters.get("fields"): 
            url += f"&fields={parameters['fields']}" 
        response = requests.get(url, headers=headers, auth=auth) 
        return response.json() 
    # Handle 'get_policies' tool 
    elif tool_name == "get_policies": 
        url = base_url + "policies" 
        query_params = [] 
        if parameters.get("policyType"): 
            query_params.append(f"policyType={parameters['policyType']}")
        if parameters.get("q"): 
            query_params.append(f"q={parameters['q']}") 
        if parameters.get("roleId"): 
            query_params.append(f"roleId={parameters['roleId']}") 
        if query_params: 
            url += "?" + "&".join(query_params) 
        response = requests.get(url, headers=headers, auth=auth) 
        return response.json() 
    # Handle 'get_role_members' example (Specific case with parameters like membershipType) 
    elif tool_name == "get_role_members": 
        role_id = parameters.get("role_id", "") 
        membership_type = parameters.get("membershipType", "DIRECT") 
        url = base_url + f"roles/{role_id}/members?membershipType={membership_type}" 
        response = requests.get(url, headers=headers, auth=auth) 
        return response.json() 
    else: return{"error": "Unknown tool_name"}

def format_users_response(response_data):
    formatted_output = "User List:\n"
    for user in response_data.get('users', []):
        user_info = user.get('fields', [])
        user_id = user.get('id', 'N/A')
        display_name = next((field['value'] for field in user_info if field['name'] == 'Display Name'), 'N/A')
        status = next((field['value'] for field in user_info if field['name'] == 'Status'), 'N/A')
        role = next((field['value'] for field in user_info if field['name'] == 'Role'), 'N/A')
        org_name = next((field['value'] for field in user_info if field['name'] == 'Organization Name'), 'N/A')
        # Format each user's details into readable format
        formatted_output += f"\nUser ID: {user_id}\n"
        formatted_output += f"Display Name: {display_name}\n"
        formatted_output += f"Status: {status}\n"
        formatted_output += f"Role: {role}\n"
        formatted_output += f"Organization: {org_name}\n"
        formatted_output += "-"*40 + "\n"
    return formatted_output

# Function to interact with the chatbot and process the user's request
def chatbot_flow(user_query, user, pwd):
    # Step 1: Pass the user query directly to Oracle GenAI
    llm_response = get_llm_response(user_query)

    # Step 2: Parse the LLM response to extract the tool name and parameters (Assumed to be structured)
    tool_name, parameters = parse_llm_response(llm_response)


    # Step 3: Execute the tool call
    tool_results = []
    output = execute_tool_call(tool_name, parameters, user, pwd)
    tool_results.append({
        "call": {"name": tool_name, "parameters": parameters},
        "outputs": [output]
    })

    # Step 4: Generate final human-readable response (returning raw output here for simplicity)
    return json.dumps(tool_results, indent=2), output

# Example usage
if __name__ == "__main__":
    user_query = input("Type in a request: \n")
    username = "USER"
    password = "pwd"
    result, output = chatbot_flow(user_query, username, password)
    #final_result = format_users_response(output)
    #print(final_result)
    print(result)
