from langchain.embeddings import HuggingFaceEmbeddings
import streamlit as st
from pymongo import MongoClient
from qdrant_client import QdrantClient, models

st.set_page_config(initial_sidebar_state="expanded")


mongodb_password = st.secrets['mongodb_password']
mongodb_username = st.secrets['mongodb_username']

mongodb_password = st.secrets['mongodb_password']
mongodb_username = st.secrets['mongodb_username']

connection_string = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.s4bz1ci.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(connection_string)
    db = client['hr_chatbot']
    collection = db['hr_chatbot']
except Exception as e:
    print(f"An error occurred while connecting to MongoDB: {e}")



openai_api_key = st.secrets['openai_api_key']

st.title("HR Interface - Delete Existing Policies")

query = {}
projection = {"policy name": 1, "source": 1, "_id": 0}
user_document = collection.find(query,projection)
user_document = list(user_document)
st.subheader("Uploaded policies table")

table = st.table(user_document)

policy_names = [doc ['policy name']for doc in user_document]

selected_policy = st.selectbox("Select the relevant policy to delete",policy_names)


if st.button("Delete Selected Policy"):
    if len(policy_names)==0:
        st.warning("Policies are not available in the knowledge base...!")
    else:
        query_delete = {"policy name":selected_policy}
        projection_delete={"source": 1, "_id": 0}
        selected_source = collection.find(query_delete,projection_delete)
        selected_source = list(selected_source)
        selected_source_path = [doc1 ['source'] for doc1 in selected_source]
        selected_source_path = selected_source_path[0]
        delete_mongo = collection.delete_many({"source":selected_source_path})
        #st.success(selected_source_path)


        qdrant_url = st.secrets['qdrant_url']
        qdrant_api_key = st.secrets['qdrant_api_key']

        client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key)
        embeddings = st.secrets['embeddings']
        #embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        collection_name="hr_chatbot" #collection_name="test_collection"

        client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.source",
                            match=models.MatchValue(value=selected_source_path),
                        ),
                    ],
                )
            ),
        )

        st.success(f"{selected_policy} is successfully deleted from the knowledge base")
           
st.warning("Contact IT Desk on 2222 or itsupportdesk@abc.com | Click www.abc.com to see the FAQ")
