import openai
import os
import pickle

from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from llama_index import download_loader

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from dotenv import load_dotenv

load_dotenv()

GDOCS_IDS = os.getenv('GDOCS_IDS')

loader_options = {
    'promts': os.getenv('HLAMIDA_PROMTS_ID'),
    'common': os.getenv('HLAMIDA_COMMON_ID'),
}


class GPT():
    def __init__(self):
        pass

    def local_load_search_indexes(self) -> str:

        with open(
            '/Users/aleksandrkulagin/Dev/chatgpt/custom_gpt/chatgpt_zone/alice.txt'
        ) as f:
            file = f.read()
        return self.create_embedding(file)

    def authorize_gdocs(self):
        google_oauth2_scopes = [
            "https://www.googleapis.com/auth/documents.readonly"
        ]
        cred = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", 'rb') as token:
                cred = pickle.load(token)
        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", google_oauth2_scopes,
                )
                cred = flow.run_local_server(port=0)
            with open("token.pickle", 'wb') as token:
                pickle.dump(cred, token)

    def google_load_search_indexes(self, option) -> str:

        self.authorize_gdocs()

        GoogleDocsReader = download_loader('GoogleDocsReader')
        gdoc_ids = [loader_options[option]]
        loader = GoogleDocsReader()
        documents = loader.load_data(document_ids=gdoc_ids)

        return self.create_embedding(documents[0].text)

    def create_embedding(self, data):
        source_chunks = []
        splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1024, chunk_overlap=0,
        )
        for chunk in splitter.split_text(data):
            source_chunks.append(Document(page_content=chunk, metadata={}))
        search_index = Chroma.from_documents(source_chunks, OpenAIEmbeddings())

        return search_index

    def answer_index(self, system, topic, search_index, temp=1):

        docs = search_index.similarity_search(topic, k=5)
        message_content = [doc.page_content for doc in docs]
        messages = [
            {"role": "system", "content": system + f"{message_content}"},
            {"role": "user", "content": topic}
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temp
        )

        return completion.choices[0].message.content


def telegram_ask(prompt):
    gpt = GPT()
    #marketing_index = gpt.local_load_search_indexes()
    marketing_index = gpt.google_load_search_indexes('common')
    marketing_chat_promt = gpt.google_load_search_indexes('promts')
    #marketing_chat_promt = '''Тебя зовут Джинни, ты - мужчина, весёлый, яркий, заводной. У тебя есть книга о достопримечательностях города, в ней же находятся твои любимые фразы.
    #Тебя просят рассказать о достопримечтельностях или услугах в городе. Если в книге нет нужной информации, расскажи, что знаешь сам. Ответ должен быть не длинным, 2-3 предложения. Если спросят о погоде - предположи или посмотри в окно.
    #В разговоре используй свои любимые фразы как можно чаще, веселись, шути. При ответе собеседнику всегда используй свои любимые обращения.
    #Книга о Сочи: '''
    return gpt.answer_index(
        marketing_chat_promt,
        prompt,
        marketing_index,
    )


#if __name__ == '__main__':
#    gpt = GPT()
#    marketing_index = gpt.load_search_indexes()
#    marketing_chat_promt = '''Ты рассказчик историй.
#У тебя есть книга сказок.
#Тебя просят рассказать историю, отвечай максимально точно по книге, не придумывай ничего от себя.
#Книга сказок: '''
#    gpt.answer_index(
#        marketing_chat_promt,
#        'Расскажи, о чём сказка?',
#        marketing_index,
#        verbose=1,
#    )
