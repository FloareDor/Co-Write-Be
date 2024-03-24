import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
import color_print
from openai import OpenAI
from constants import OPENAI_API_KEY
os.environ['OPENAI_API_KEY']=OPENAI_API_KEY
from machine import predict_sentence
from machine import cv, spam_detect_model

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(max_history_len=3, ai_limitation="Default", highlighted_text="", user_query="", assignment_id=""):
    try:
        if user_query == "":
            return ""
        predicted_label = predict_sentence(user_query, cv, spam_detect_model)
        if predicted_label == 0:
            return "User is providing complete work. No response generated."
        
        # Construct final prompt based on AI limits, highlighted text, and user query
        prompt = "Ensure that the response does not exceed 100 words.\nProvide responses that maintain a professional and respectful tone.\n"
        if ai_limitation != "Default":
            prompt += ai_limitation
        # elif ai_limitation == "Professor":
        #     prompt = "[Professor AI Limits and customization]\n\nDon't help with code.\n\nAvoid directly copying verbatim text from the input document."   

        prompt += f"\n\n[User's Highlighted text]\n\n{highlighted_text}\n\n[User Message]\n\nUser: {user_query}\n\n"

        # Load the vector store and embeddings
        try:
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.load_local(f"embeddings/{assignment_id}", embeddings=embeddings, allow_dangerous_deserialization=True)
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
	
def get_pdf_paths(folder_path):
    """Returns a list of the paths of all the PDFs in the given folder."""
    pdf_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_paths.append(os.path.join(root, file))
    return pdf_paths

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

@app.get("/index")
async def index(assignment_id):
    try:
        """Read pdfs from docs folder and index them in vector database"""
        print("starting indexing...")
        folder_path = f"docs/{assignment_id}"
        text = []
        for path in get_pdf_paths(folder_path):
            print(path)
            loader = PyPDFLoader(path)
            text.extend(loader.load())
            print(f"Read data of file: {path}")
            os.remove(path=path)
        print("Creating text chunks...")
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=400, chunk_overlap=50, length_function=len)
        text_chunks = text_splitter.split_documents(text)
        print("creating embeddings")
        embeddings = OpenAIEmbeddings()
        if os.path.isdir(f"embeddings/{assignment_id}"):
            print(f'embeddings/{assignment_id} exists, loading')
            vectorstore = FAISS.load_local(f"embeddings/{assignment_id}", embeddings=embeddings)
            print("adding tof embeddings/{assignment_id}")
            vectorstore.add_documents(text_chunks)
            print("savingf embeddings/{assignment_id}")
            vectorstore.save_local(f"embeddings/{assignment_id}")
        else:
            print(f"embeddings/{assignment_id} does not exists, creating")
            vectorstore = FAISS.from_documents(text_chunks, embeddings)
            print("saving locally")
            vectorstore.save_local(f"embeddings/{assignment_id}")
        print("Docs indexed successfully!!")
        return JSONResponse(content={"message": "Docs indexed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": e}, status_code=500)

# if __name__ == "__main__":
# 	print(chat(user_query="Do my assignment", docname="amaan-1234"))
        
# We need to make this an api!!!!

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)