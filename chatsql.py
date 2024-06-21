from dotenv import load_dotenv
import gradio as gr
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///Ramen.db")
print(db.dialect)
print(db.get_usable_table_names())

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def predict(message, history):
    agent_executor = create_sql_agent(llm, db=db, 
                                      agent_type="openai-tools", 
                                      verbose=True)

    res = agent_executor.invoke({"input": message})

    print(res)
    print()
    print(res['output'])
    return res['output']


message = "When was the most recent alert for the customer Wonderful citrus and provide a link for the video clip"
gr.ChatInterface(predict, 
                 chatbot=gr.Chatbot(height=400),
                 textbox=gr.Textbox(placeholder='Ask me a question', scale=7, container=False),
                 title='Welcome to Ramen Eye Chat',
                 description='I know about all the Ramen Eye customers, '+
                 'their camera deployments and the alerts generated.\n\n'+
                 'Ask me a question about any of these ...',
                 examples=['How many cameras?', 'How many alerts?', 
                           'Give me details of the most recent alert',
                           'Give me video link of the most recent alert'],
                 retry_btn=None,
                 undo_btn=None,
                 clear_btn=None
                 ).launch(share=True)