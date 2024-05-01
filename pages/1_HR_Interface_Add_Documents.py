from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
import streamlit as st
import os
import shutil
from pymongo import MongoClient
from urllib.parse import quote_plus

st.set_page_config(initial_sidebar_state="expanded")

openai_api_key = st.secrets['openai_api_key']

mongodb_password = st.secrets['mongodb_password']
mongodb_username = st.secrets['mongodb_username']

mongopassword = quote_plus(mongodb_password)
connection_string = f"mongodb+srv://{mongodb_username}:{mongopassword}@cluster0.s4bz1ci.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(connection_string)
    db = client['hr_chatbot']
    collection = db['hr_chatbot']
except Exception as e:
    print(f"An error occurred while connecting to MongoDB: {e}")

try:
    client = MongoClient(connection_string)
    db = client['hr_chatbot']
    collection2 = db['feedback']
except Exception as e:
    print(f"An error occurred while connecting to MongoDB: {e}")


st.title("HR Interface - Upload Policies")

temp_folder = "temp"
os.makedirs(temp_folder, exist_ok=True)

# Upload Document
uploaded_files = st.file_uploader("Upload the policies",accept_multiple_files=True,type="pdf")

if st.button("Upload selected files"):

  if uploaded_files:
    currentpath = os.getcwd()
    directory = os.path.join(currentpath,"temp")
    for uploaded_file in uploaded_files:
        # Save the file to the temporary folder
        output_temp_file_path = os.path.join(temp_folder, uploaded_file.name)
        meta_data = {"policy name":uploaded_file.name,"file path":directory, "source":directory+"/"+uploaded_file.name}
        result = collection.insert_one(meta_data)

        with open(output_temp_file_path, 'wb') as output_temp_file:
            output_temp_file.write(uploaded_file.read())
          
    #st.success(directory)

    loader = PyPDFDirectoryLoader(directory)
    docs = loader.load_and_split()
    docs_count = (len(docs))

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, 
                                                chunk_overlap=20,
                                                length_function = len,
                                                separators=['\n\n', '\n', '.', ' ', ''],
                                                add_start_index = True,
                                                )
    
    text_chunks = text_splitter.split_documents(docs)


    #embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    qdrant_url = st.secrets['qdrant_url']
    qdrant_api_key = st.secrets['qdrant_api_key']
  
    qdrant = Qdrant.from_documents(
      text_chunks,
      embeddings,
      url=qdrant_url,
      prefer_grpc=True,
      api_key=qdrant_api_key,
      collection_name="hr_chatbot", #collection_name="test_collection"
      )

    shutil.rmtree(directory)
    st.success(f"Selected policy/policies uploaded successfully....!")


query2 = {}
projection2 = {"score": 1, "text":1,"_id": 0}
user_document2 = collection2.find(query2,projection2)
user_document2 = list(user_document2)
st.subheader("Feedback table")

table = st.table(user_document2)

st.warning("Contact IT Desk on 2222 or itsupportdesk@abc.com | Click www.abc.com to see the FAQ")
