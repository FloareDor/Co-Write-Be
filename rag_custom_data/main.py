import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
import color_print
from constants import OPENAI_API_KEY
os.environ['OPENAI_API_KEY']=OPENAI_API_KEY


def main():
    try: 
        # check whether index has been already created
        if not os.path.isdir("pdf-index"):
            color_print.print_red("Index some data to get started")
            print("""
            You can add the pdfs you want to index in docs folder,
            then execute the index.py file to index the pdf into vector database
            """)
            return
        
        # set the length of history
        max_history_len = 3
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("pdf-index", embeddings=embeddings, allow_dangerous_deserialization=True)
        llm = ChatOpenAI()
        history = []
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type='stuff',
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )
        while(1):
            query = color_print.print_green("Enter Your query")
            query = input()
            resp = chain({"question": query, "chat_history": history})
            history.append((query, resp["answer"]))
            while len(history)>max_history_len:
                history.pop(0)

            color_print.print_green("Answer")
            print(resp["answer"])

            color_print.print_green("Source documents")
            # print(resp['source_documents'], "\n\n")
    except Exception as e:
        color_print.print_red(e)

def get_openai_result(query, max_history_len=3):
    try:
        # Load the vector store and embeddings
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("pdf-index", embeddings=embeddings, allow_dangerous_deserialization=True)

        # Initialize the language model and history
        llm = ChatOpenAI()
        history = []

        # Create the conversational retrieval chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type='stuff',
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

        # Get the response from the language model
        resp = chain({"question": query, "chat_history": history})
        history.append((query, resp["answer"]))

        # Truncate the history to the specified length
        while len(history) > max_history_len:
            history.pop(0)

        return resp["answer"]

    except Exception as e:
        color_print.print_red(e)
        return "An error occurred while processing your query."
    
def get_openai_result2(query, max_history_len=3, ai_limits="Default", highlighted_text="", user_query=""):
    try:
        if user_query == "":
            return ""
        # Construct final prompt based on AI limits, highlighted text, and user query
        prompt = "Ensure that the response does not exceed 500 words.\nProvide responses that maintain a professional and respectful tone.\n"
        if ai_limits != "Default":
            prompt += ai_limits
        # elif ai_limits == "Professor":
        #     prompt = "[Professor AI Limits and customization]\n\nDon't help with code.\n\nAvoid directly copying verbatim text from the input document."
            

        prompt += f"\n\n[User's Highlighted text]\n\n{highlighted_text}\n\n[User Message]\n\nUser: {user_query}\n\n"

        # Load the vector store and embeddings
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("pdf-index", embeddings=embeddings, allow_dangerous_deserialization=True)

        # Initialize the language model and history
        llm = ChatOpenAI()
        history = []

        # Create the conversational retrieval chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type='stuff',
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True
        )

        # Get the response from the language model
        resp = chain({"question": query, "chat_history": history}, prompt=prompt)
        history.append((query, resp["answer"]))

        # Truncate the history to the specified length
        while len(history) > max_history_len:
            history.pop(0)

        return resp["answer"]

    except Exception as e:
        color_print.print_red(e)
        return "An error occurred while processing your query."



if __name__=="__main__":
    color_print.print_green("LLMs on Custom Data")
    main()
