# RAEN CrewAI Tools

This repository provides [CrewAI](https://crewai.com) tool wrappers for the **RAEN MCP Gateway**. These tools allow AI agents to programmatically draft legal dispute letters and analyze contracts using RAEN's specialized legal models.

## Features

- **`dispute_letter_tool`**: Generates professional dispute letters based on provided context.
- **`contract_analyze_tool`**: Extracts risks and key information from legal documents.
- **Seamless Integration**: Built using CrewAI's `@tool` decorator for easy agent assignment.

## Installation

1. Clone this repository or copy the files to your project.
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You need a **RAEN MCP Dev Key** to use these tools. 
Set it as an environment variable or pass it directly to the initialization function:

```python
from raen_crew_tools import init_raen_client
init_raen_client("your_raen_dev_key_here")
```

## Usage Example

```python
from crewai import Agent, Task, Crew
from raen_crew_tools import dispute_letter_tool, init_raen_client

init_raen_client("YOUR_KEY")

agent = Agent(
    role='Legal Assistant',
    goal='Draft letters',
    tools=[dispute_letter_tool],
    backstory='Expert in legal writing'
)

# Define tasks and crew as usual...
```

## About RAEN
RAEN is a fleet of agentic services. This integration connects to the MCP Gateway at `https://raen-mcp-gateway.fly.dev/mcp`.
