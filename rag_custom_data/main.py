import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
import color_print
from constants import OPENAI_API_KEY
os.environ['OPENAI_API_KEY']=OPENAI_API_KEY
from machine import predict_sentence
from machine import cv, spam_detect_model
from openai import OpenAI

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
        vectorstore = FAISS.load_local("pdf-index", embeddings=embeddings)
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
            predicted_label = predict_sentence(query, cv, spam_detect_model)
            if predicted_label == 1:
                resp = chain({"question": query, "chat_history": history})
                history.append((query, resp["answer"]))
                while len(history)>max_history_len:
                    history.pop(0)

                color_print.print_green("Answer")
                print(resp["answer"])

                color_print.print_green("Source documents")
                print(resp['source_documents'], "\n\n")
            else:
                color_print.print_yellow("User is providing complete work. No response generated.")
    except Exception as e:
        color_print.print_red(e)

def chat(max_history_len=3, ai_limits="Default", highlighted_text="", user_query="", docname=""):
    try:
        if user_query == "":
            return ""
        predicted_label = predict_sentence(user_query, cv, spam_detect_model)
        if predicted_label == 0:
            return "User is providing complete work. No response generated."
        
        # Construct final prompt based on AI limits, highlighted text, and user query
        prompt = "Ensure that the response does not exceed 100 words.\nProvide responses that maintain a professional and respectful tone.\n"
        if ai_limits != "Default":
            prompt += ai_limits
        # elif ai_limits == "Professor":
        #     prompt = "[Professor AI Limits and customization]\n\nDon't help with code.\n\nAvoid directly copying verbatim text from the input document."   

        prompt += f"\n\n[User's Highlighted text]\n\n{highlighted_text}\n\n[User Message]\n\nUser: {user_query}\n\n"

        # Load the vector store and embeddings
        try:
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.load_local(f"pdf-index{docname}", embeddings=embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            color_print.print_red(f"Error: {e}")
            # normal gpt bro
            print("No embeddings found for this assignment.")
            return normal_gpt(prompt)

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
        resp = chain({"question": prompt, "chat_history": history})
        history.append((prompt, resp["answer"]))

        # Truncate the history to the specified length
        while len(history) > max_history_len:
            history.pop(0)

        return resp["answer"]
    


    except Exception as e:
        color_print.print_red(e)
        return "An error occurred while processing your query."
    

def normal_gpt(prompt):
    # Set OpenAI API key programmatically

    # Set OpenAI API key for the OpenAI client
    OpenAI.api_key = OPENAI_API_KEY

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content

    # print(completion.choices[0].message.content)


if __name__=="__main__":
    # color_print.print_green("LLMs on Custom Data")
    # main()
    print(chat(user_query="Help with understanding photosynthesis.", docname="/amaan-12342r31tr"))
    

