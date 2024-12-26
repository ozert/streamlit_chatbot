import sys
import os

sys.path.append(os.getcwd())

from chains.chains import Chains


############################################ TEMP
import random

def generate_random_int(min_value=0, max_value=10000):
  """Generates a random integer within the specified range (inclusive)."""
  return random.randint(min_value, max_value)


############################################ TEMP


def generate_response(conversation_history:list):
    #return "This is a placeholder."

    llm_chain = Chains(model_name="gpt-3.5-turbo")
    
    context = "\n".join(f"{key.capitalize()}: {value}" for d in conversation_history for key, value in d.items())
    last_user_prompt = conversation_history[-1]["content"]
    response = llm_chain.route_user_query_to_chains(conversation_history=context, last_user_prompt=last_user_prompt)
    
    return response

def summarize_conversation(conversation_history:list):
    llm_chain = Chains(model_name="gpt-3.5-turbo")
    
    context = "\n".join(f"{key.capitalize()}: {value}" for d in conversation_history for key, value in d.items())
    conversation_summary = llm_chain.summarize_conversation(conversation_history=context)

    return conversation_summary


if __name__ == "__main__":
    simulation_of_a_conversation_history = [{'role': 'user', 'content': 'hii'}, {'role': 'assistant', 'content': 'This is a placeholder.'}]
    conversation_summary = summarize_conversation(conversation_history=simulation_of_a_conversation_history)
    print(conversation_summary["summary"])