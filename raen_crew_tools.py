import requests
from typing import Any, Dict, Optional
from crewai.tools import tool
from pydantic import BaseModel, Field

class RAENMCPClient:
    """Client to interact with the RAEN MCP Gateway."""
    def __init__(self, api_key: str, base_url: str = "https://raen-mcp-gateway.fly.dev/mcp"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Calls a specific tool on the RAEN MCP Gateway."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # Handling MCP standard response format
            if "result" in result and "content" in result["result"]:
                return str(result["result"]["content"])
            return str(result)
        except Exception as e:
            return f"Error calling RAEN tool {tool_name}: {str(e)}"

# Global client instance (to be initialized with the dev key)
# In a production scenario, this would be managed via environment variables
raen_client: Optional[RAENMCPClient] = None

def init_raen_client(api_key: str):
    global raen_client
    raen_client = RAENMCPClient(api_key)

@tool("dispute_letter_tool")
def dispute_letter_tool(context: str) -> str:
    """
    Drafts a formal legal dispute letter. 
    Input should be a detailed description of the dispute, including parties involved, 
    dates, and the specific reason for the dispute.
    """
    if not raen_client:
        return "Error: RAEN Client not initialized. Please provide an API Key."
    
    return raen_client.call_tool("dispute_letter", {"context": context})

@tool("contract_analyze_tool")
def contract_analyze_tool(contract_text: str) -> str:
    """
    Analyzes a legal contract to identify risks, key clauses, and obligations.
    Input should be the full text of the contract or a detailed summary.
    """
    if not raen_client:
        return "Error: RAEN Client not initialized. Please provide an API Key."
    
    return raen_client.call_tool("contract_analyze", {"contract_text": contract_text})
