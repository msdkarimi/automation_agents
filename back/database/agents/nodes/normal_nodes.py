from states import CustomMessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import re
from langchain_ollama.chat_models import ChatOllama

def get_llm(OLLAMA_BASE_URL="http://localhost:11434", LLM_MODEL_NAME = 'qwen3:1.7b'):
    return ChatOllama(base_url=OLLAMA_BASE_URL, model=LLM_MODEL_NAME, temperature=0.0)






def interaction(state: CustomMessagesState)-> CustomMessagesState:
    print('--------------------------------------------------------')
    # a_msg = SystemMessage('you are helpful assitant in generating python codes.')
#
    # state['messages'] = [a_msg]
    h_msg = HumanMessage(state['prompt'])

    new_msgs =  [h_msg]

    AIresponse = get_llm().invoke([state['messages'][-1]] + new_msgs)

    match = re.search(r'<think>(.*?)</think>(.*)', AIresponse.content, re.DOTALL)
    think_text = match.group(1).strip() if match else ''
    response_text = match.group(2).strip() if match else ''

    return {'messages': new_msgs + [AIMessage(response_text)]}

