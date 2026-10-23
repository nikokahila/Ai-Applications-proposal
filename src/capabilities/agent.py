"""
Optional project capability: Agent Workflows.

Implement this module only if this capability is relevant to your application's
user problem. Remove the file if the capability is not used.

Conceptual Overview:
-------------------
Practical agentic behavior involves iterative execution loops where the model selects actions
based on observations, while application code maintains control over available actions,
validation rules, and stopping conditions.

Key concepts when implementing agentic workflows:
1. Model-Selected Actions: The LLM analyzes the current state/observation and chooses
   the next step from a defined set of actions.
2. Controlled Loop: Application code manages the execution loop (Observation -> Decision -> Action -> Observation).
3. Explicit Boundaries & Stopping Conditions: Application code enforces maximum iterations,
   error limits, and final completion conditions to prevent infinite loops.

Note:
-----
An agent pattern should only be used when dynamic, model-selected sequence of actions is
genuinely required by the user problem. Avoid unneeded complexity.
"""

# Implement custom agent loop logic below if selected.

import json
import ollama
from src.capabilities.tools import AVAILABLE_TOOLS, search_recipes_with_ai

class KitchenAgent:
    def __init__(self, model_name: str = "llama3.2"):  # Varmista että malli löytyy koneeltasi (esim. llama3.2 tai mistral)
        self.model_name = model_name

    def chat(self, user_message: str) -> str:
        """Processes the user message, calls the RAG tool if necessary, and returns the response."""
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart and helpful AI Kitchen Assistant. "
                    "Your task is to help the user find recipes from the database by using the available tools."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        try:
            # Call Ollama and provide the RAG tool
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=[search_recipes_with_ai]
            )
            
            # Check if the model wants to call the RAG tool
            if response.get('message', {}).get('tool_calls'):
                for tool in response['message']['tool_calls']:
                    function_name = tool['function']['name']
                    function_args = tool['function']['arguments']
                    
                    print(f"\n-> [AGENT CALLING RAG TOOL]: {function_name} args: {function_args}")
                    
                    if function_name in AVAILABLE_TOOLS:
                        # Execute the RAG search from PP_recipes.csv
                        tool_result = AVAILABLE_TOOLS[function_name](**function_args)
                        
                        # Feed the results back to the model so it can format the final answer
                        messages.append(response['message'])
                        messages.append({'role': 'tool', 'content': tool_result})
                        
                        final_response = ollama.chat(model=self.model_name, messages=messages)
                        return final_response['message']['content']
            
            # If no tool was needed, return the direct response
            return response["message"]["content"]

        except Exception as e:
            return f"Error running AI model (make sure Ollama is running): {str(e)}"