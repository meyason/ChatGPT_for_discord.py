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


class api_setter():
    def api(api_key):
        openai.api_key = os.environ[api_key]
    
class gpt_one_response():
    def __init__(self, api_key, model_name = "gpt-3.5-turbo-16k", content = "あなたは優秀なアシスタントです．"):
        self.model = model_name
        self.content = content
        api_setter.api(api_key)
    
    def calling(self, text):
        response = openai.ChatCompletion.create(
            model = self.model,
            messages=[
                {"role": "system", "content": self.content},
                {"role": "user", "content": text},
            ]
        )
        return response["choices"][0]["message"]["content"]

class gpt_with_langchain():
    def __init__(self, api_key):
        self.API_KEY = api_key
        api_setter.api(api_key)
        
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
                        model_name="gpt-3.5-turbo-16k",
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

        # discordの送信制限:2000文字
        if len(response) > 2000:
            one_r = gpt_one_response(self.API_KEY, content = "あなたは入力した文章を1950字で要約します．")
            summary = one_r.calling(response)
            response = summary["choices"][0]["message"]["content"]

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