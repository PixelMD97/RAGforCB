import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI

def load_or_build_qa_chain():
    # Load all PDF files in the "data" folder
    loaders = [PyPDFLoader(os.path.join("data", f)) for f in os.listdir("data") if f.endswith(".pdf")]
    docs = [doc for loader in loaders for doc in loader.load()]

    # Split documents into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    # Create vectorstore from chunks
    vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())

    # Set up retriever
    retriever = vectorstore.as_retriever()

    # Initialize ChatOpenAI with German-friendly settings
    chat_model = ChatOpenAI(
        model="gpt-4",
        temperature=0,
    )

    # Define prompt to always answer in German
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        Du bist ein klinischer Studienassistent. Beantworte die folgende Frage basierend auf den bereitgestellten Dokumenten **auf Deutsch**.

        Kontext:
        {context}

        Frage: {question}
        """
    )

    # Set up RetrievalQA with German prompt
    return RetrievalQA.from_chain_type(
        llm=chat_model,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
