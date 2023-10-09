import openai
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import docx2txt

# Load environment variables
# load_dotenv()
api_key = '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'


def process_text(text):
    # Split the text into chunks using Langchain's CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Convert the chunks of text into embeddings to form a knowledge base
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    knowledgeBase = FAISS.from_texts(chunks, embeddings)

    return knowledgeBase


def main():
    st.title("Chat with your PDF 💬")

    pdf = st.file_uploader('Upload your PDF Document', type=["pdf", "docx"])

    if pdf is not None:
        if pdf.type == 'pdf':
            pdf_reader = PdfReader(pdf)
            # Text variable will store the pdf text
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        else:
            text = docx2txt.process(pdf)
        # Create the knowledge base object
        knowledgeBase = process_text(text)

        query = st.text_input('Ask a question to the PDF')
        cancel_button = st.button('Cancel')

        if cancel_button:
            st.stop()

        if query:
            docs = knowledgeBase.similarity_search(query)

            llm = OpenAI(openai_api_key=api_key)
            chain = load_qa_chain(llm, chain_type='stuff')

            with get_openai_callback() as cost:
                response = chain.run(input_documents=docs, question=query)
                print(cost)

            st.write(response)


if __name__ == "__main__":
    main()
