import os
from crewai import Agent, Task, Crew, Process
from raen_crew_tools import dispute_letter_tool, contract_analyze_tool, init_raen_client

# 1. Initialize the RAEN Client with your Dev Key
# The key is provided by RAEN upon bounty claim/merge
RAEN_DEV_KEY = os.getenv("RAEN_DEV_KEY", "YOUR_DEV_KEY_HERE")
init_raen_client(RAEN_DEV_KEY)

# 2. Define the Agent
legal_agent = Agent(
    role='Legal Automation Specialist',
    goal='Analyze contracts and draft high-quality dispute letters for clients.',
    backstory="""You are an expert legal assistant specialized in consumer rights 
    and contract law. You use RAEN tools to provide accurate and professional 
    legal documentation.""",
    tools=[dispute_letter_tool, contract_analyze_tool],
    verbose=True,
    allow_delegation=False
)

# 3. Define the Tasks
analysis_task = Task(
    description="""Analyze the following contract snippet for potential risks: 
    'The provider reserves the right to increase fees by 50% without prior notice.'""",
    expected_output="A detailed risk report based on the contract analysis.",
    agent=legal_agent
)

dispute_task = Task(
    description="""Draft a dispute letter for a customer whose gym membership 
    was charged twice this month ($100 total) and the gym refuses to refund.""",
    expected_output="A professional dispute letter ready to be sent.",
    agent=legal_agent
)

# 4. Form the Crew
crew = Crew(
    agents=[legal_agent],
    tasks=[analysis_task, dispute_task],
    process=Process.sequential
)

# 5. Execute
print("### Starting RAEN CrewAI Flow ###")
result = crew.kickoff()

print("\n\n########################")
print("## FINAL OUTPUT ##")
print("########################\n")
print(result)
