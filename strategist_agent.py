import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Define the System Prompt
system_prompt = """
You are the 'Strategist Agent' for Makhan Move, an AI relocation platform in India.
Your job is to take user move requirements and output a strict negotiation strategy for our Voice Agent to use when calling local truck drivers.

You MUST include questions about Indian-specific hidden costs based on the route.
Output ONLY a valid JSON object with the following keys:
- target_price: (integer) Estimated fair price in INR.
- negotiation_angle: (string) A 1-sentence strategy.
- hidden_cost_questions: (list of strings) 3 specific questions to ask the mover to avoid scams.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "User Requirements: {requirements}")
])

chain = prompt | llm

# Test the Agent
if __name__ == "__main__":
    test_requirements = {
        "pickup": "Koramangala, Bangalore",
        "drop": "DLF Phase 3, Gurgaon",
        "inventory": "2BHK, includes a fridge and washing machine",
        "date": "Next Friday"
    }
    
    response = chain.invoke({"requirements": str(test_requirements)})
    print(response.content)