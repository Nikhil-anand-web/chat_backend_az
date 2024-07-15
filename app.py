from flask import Flask, jsonify, request, session, make_response
from flask_session import Session
import redis
import os

import json
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain.vectorstores import  FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from flask_cors import CORS
from flask_cors import cross_origin
load_dotenv()

app = Flask(__name__)
app.secret_key = '9g743y-@9ogh3n82f'
app.config['SESSION_TYPE'] = 'redis'
# Session data doesn't persist beyond browser session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='localhost',  # Replace with your Redis server's host
    port=6379,          # Replace with your Redis server's port
    db=0                # Replace with the Redis database number (default is 0)
)
Session(app)
CORS(app, resources={
     r"/api/*": {"origins": "*", "supports_credentials": True}})

os.environ["OPENAI_API_KEY"] = "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"


embeddings = OpenAIEmbeddings()
new_db1 = FAISS.load_local("main_DB/mega_Base1", embeddings)


@app.route('/', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def home():

    if request.method == 'POST':

        try:

            if not session.get('hello'):
                print("run")
                session['hello'] = ConversationalRetrievalChain.from_llm(
                    llm=OpenAI(temperature=0.6),
                    retriever=new_db1.as_retriever(),
                    memory=ConversationBufferMemory(
                        memory_key='chat_history', return_messages=True)
                )

            data = json.loads(request.data.decode('utf-8'))
            # Retrieve the question from the JSON data.

            question = data.get('question', '')

            chain = session.get('hello')
            lis = []

            if question:

                response = chain({'question': question})
                res = response['chat_history']

                questionn = ""
                answerr = ""

                for i, message in enumerate(res):
                    if i % 2 == 0:
                        questionn = message.content
                    else:
                        answerr = message.content
                        if answerr:
                            lis.append({questionn: answerr})

                act = make_response(jsonify(lis))

                return act

        except Exception as e:
            print(e)
            return jsonify({"error": "something went wrong"})
    else:
        session.pop('hello', default=None)
        return "cleared"


app.run(host='0.0.0.0', port=8000, debug=True)
