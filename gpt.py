import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackManager
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory

import pickle
import os
memory_path = "memory"
if not os.path.exists(memory_path):
    os.makedirs(memory_path)

class chatgptorg():
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.template = """あなたはDiscordのbotで，暇つぶし相手です．以下は過去に行ったやり取りです．
        {history}
        human : {human_input}
        Assistant :
        """

    # メモリを組み込んだLangChainの初期化
    def launch_chain(self, memory):
        self.prompt = PromptTemplate(template=self.template,
                                input_variables = ["history", "human_input"])
        
        self.chain = LLMChain(
            llm = ChatOpenAI(streaming= True,
                        model_name="gpt-3.5-turbo-1106",
                        callback_manager=BaseCallbackManager([StdOutCallbackHandler()]),
                        openai_api_key=self.API_KEY),
            prompt = self.prompt,
            memory = memory,
            verbose=True
        )
        return self.chain

    # メモリの初期化
    def launch_memory(self):
        memory = ConversationBufferMemory()
        return memory

    # GPTによる応答
    def output(self, server_id, text):
        memory = self.launch_memory()

        filename = f"{memory_path}/{server_id}.pkl"

        if os.path.exists(filename):
            memory.chat_memory.messages = self.load_history(server_id)
        else:
            print("make memory")
            self.reset_history(server_id)

        response = self.launch_chain(memory).predict(human_input=text)

        self.save_history(server_id, memory.chat_memory.messages)

        return response

    # メモリをpklファイルに保存
    def save_history(self, server_id, messages):
        history_dict = messages_to_dict(messages)
        filename = f"{memory_path}/{server_id}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(history_dict, f)

    # pklファイルからメモリを読み込み
    def load_history(self, server_id):
        filename = f"{memory_path}/{server_id}.pkl"
        with open(filename, "rb") as f:
            history_dicts = pickle.load(f)
        return messages_from_dict(history_dicts)
    
    # pklファイルの初期化
    def reset_history(self, server_id):
        ini_dict = {}
        filename = f"{memory_path}/{server_id}.pkl"
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "wb") as f:
            pickle.dump(ini_dict, f)