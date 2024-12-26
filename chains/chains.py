from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers.json import SimpleJsonOutputParser
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.getcwd())

from prompts.generic_questions import GenericQuestionTemplate
from prompts.financial_questions import FinancialQuestionTemplate
from prompts.summarization import SummarizationTemplate
from prompts.chain_router import ChainRouterTemplate

class Chains():
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model = ChatOpenAI(model=model_name)
        self.summary_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SummarizationTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(SummarizationTemplate.USER_PROMPT)])
        
        self.json_parser = SimpleJsonOutputParser()
        self.string_output_parser = StrOutputParser()

        self.generic_questions_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(GenericQuestionTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(GenericQuestionTemplate.USER_PROMPT)])

        self.financial_questions_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(FinancialQuestionTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(FinancialQuestionTemplate.USER_PROMPT)])

        self.question_routing_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(ChainRouterTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(ChainRouterTemplate.USER_PROMPT)])

    def summarize_conversation(self, conversation_history:dict):
        runnable = self.summary_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(conversation_history)
        
        return response
    
    def route_user_query_to_chains(self, conversation_history: dict, last_user_prompt:str):
        # Step 1: Invoke the routing template to determine the category
        routing_runnable = self.question_routing_prompt_template | self.model | self.json_parser
        routing_chain = RunnableSequence(routing_runnable)
        routing_response = routing_chain.invoke(last_user_prompt)

        # Extract the category from the JSON response
        category = routing_response.get("category")  # Assume routing response has a key 'category'

        # Step 2: Route to the appropriate chain based on the category
        if category == "finance":
            selected_runnable = self.financial_questions_prompt_template | self.model | self.string_output_parser
        elif category == "generic":
            selected_runnable = self.generic_questions_prompt_template | self.model | self.string_output_parser

        # Step 3: Create and invoke the selected chain
        selected_chain = RunnableSequence(selected_runnable)
        final_response = selected_chain.invoke(conversation_history)

        return final_response