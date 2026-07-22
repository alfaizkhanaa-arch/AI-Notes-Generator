from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq 
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
import tempfile
from pydantic import BaseModel,Field
from typing import List
from langchain.chat_models import init_chat_model

load_dotenv()

class QuizQuestion(BaseModel) :
    question : str   = Field(description="Quiz Question")
    option :  List[str] =  Field(description=" 4 answer  option A B C D")
    answer:  str  = Field(description="Correct answer A B C D")
    explanation :  str = Field(description="Why this is correct")
    
    
class Flashcard(BaseModel):
    front :  str =  Field(description="Question or term")
    back : str =  Field(description="Answer or defination")
    topic : str  = Field(description="Topic Name")
    
    
class KeyPoints(BaseModel):
    topic : str = Field(description="Topic name") 
    key_points : List[str] =  Field(description="List of key points")   
    exam_tips : List[str] = Field(description="Tips for exam")
    difficulty :  str = Field(description="Easy Medium Hard")
    
    
    
def load_llm():
    print("[INFO] Loading LLM ..")
    llm =  init_chat_model(
       "groq:llama-3.1-8b-instant"
    )
    print("[SUCCESS] LLM Loaded!")
    return llm    
    
def load_embbedings():
    print("[INFO] Loading Emnbeddings ..")
    embeddings =  HuggingFaceEmbeddings(
        model_name    = "all-MiniLM-L6-v2",
        model_kwargs  = {"device": "cpu"},
        encode_kwargs = {"normalize_embeddings": True}
    )
    print("[SUCCESS] Embeddings loaded!")
    return embeddings

def load_documnents(file_path,file_name):
    ext =  os.path.splitext(file_name)[1].lower()
    print(f"[INFO]Loading {file_name} ({ext})")
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path,encoding='utf-8')
    else:
        raise ValueError(
            f"UnSupported {ext} file"
            f"Supported PDF OR TXT Files"
        )
    docs =  loader.load()
    print(f"{file_name} Loaded!")
    return docs

def process_notes(uploaded_files,embeddings):
    all_docs = []
    for uploaded_file in uploaded_files:
        tmp_path  = None
        try: 
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix = ext
            ) as tmp :
                tmp.write(uploaded_file.read())
                tmp_path  = tmp.name
            docs = load_documnents(
                tmp_path,
                uploaded_file.name
            )
            for doc in docs :
                doc.metadata["source"] = uploaded_file.name
            all_docs.extend(docs)
            print(f"[SUCCESS] {uploaded_file.name} loaded")
        except Exception as e :
            print(f"[ERROR] {uploaded_file.name} : {str(e)}")
            continue
                
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    if len(all_docs) == 0 :
       raise ValueError(
           "No documents loaded \n"
           "Please upload study notes PDF or TXT."
       )
    splitter =  RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100,
        separators= [
            "=====================================",
            "\n\n",
            "\n",
            " ",
            ""
        ]
    )
    chunks =  splitter.split_documents(all_docs)
    chunks = [
        c for c in chunks if c.page_content.strip()
    ]
    
    print(f"INFO valid chunks : {len(chunks)}")
    if len(chunks) == 0 :
        raise ValueError(
            "No valid chunks found \n"
            "please check your documents"
            
        )
        
    print("[INFO] Creating vector store...")
    
    vectorstore= Chroma.from_documents(
        documents= chunks,
        embedding= embeddings,
        collection_name="study_collection"
    )
    print("[SUCCESS] Study vector store created")
    return vectorstore , chunks



def bulid_qa_chain(vectorstore,llm):
    print("[INFO] Buliding Q&A chain...")
    retriever = vectorstore.as_retriever(
         search_type   = "similarity",
         search_kwargs = {"k": 3}
        
    )
    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
    You are a helpful study assistant.
    Answer questions based on the study notes provided.

    Rules:
    - Answer clearly and accurately.
    - Use examples from the notes.
    - If the answer is not in the notes, say so.
    - Keep answers concise.
    - Use bullet points when helpful.

    Context:
    {context}
    """
    ),
    ("human", "{question}")
])
    def formate_docs(docs):
        return "\n\n-------\n\n".join([
            f"[Source : {doc.metadata.get('source','Unknown')} ]\n"
            f"{doc.page_content}"
            for doc in docs
        ])
        
    chain =  (
        {
            "context" :  retriever | formate_docs,
            "question" :RunnablePassthrough()  
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    print("[SUCCESS] Q&A chain bulit!")
    return chain,retriever


def genrate_quiz(topic,chunks,llm,num_question = 5):
    
    print(f"[INFO] Generating quiz on : {topic}")
    topic_content = "\n".join(
        c.page_content
        for c in chunks
        if topic.lower() in c.page_content.lower()
        
    )[:2000]
    if not  topic_content:
        topic_content ="\n".join([
            c.page_content for c in chunks[:5]
        ])[:2000]
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Create {num} multiple choice quiz questions
        from these study notes.

        Format EXACTLY like this for each question:

        Q1: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Answer: [A/B/C/D]
        Explanation: [Why this is correct]

        Make questions test understanding
        not just memorization.
        """),
        ("human", "Notes:\n{content}")
    ])
    chain =  prompt |llm | StrOutputParser()
    result = chain.invoke({
        "num" : num_question,
        "content" :  topic_content
    })
    return result

def generate_flashcards(topic,chunks,llm):
    print(f"[INFO] Generating flashcard :{topic}")
    topic_content = "\n".join([
        c.page_content
        for  c in chunks
        if topic.lower() in c.page_content.lower()
    ])[:1500]
    
    if not topic_content :
        topic_content ="\n".join([
            c.page_content for c in chunks[:3]
            
        ])[:1500]
        
    prompt  =  ChatPromptTemplate.from_messages([
        ("system", """
         
            Create 8 flashcards from these notes.
            Formate EXACTLY like this : 
            
            CARD 1 :
                Front  : [Term or Question]
                Back :  [Definition or Answer]
         
            CARD 2 : 
                Front  : [Term or Question]
                Back :  [Definition or Answer]
            Focus  on key terms and conecpts.
            Keep answer brief  and clear.
            
         """),
        ("human", "Notes\n {content}")
        
    ])
    chain  = prompt |  llm | StrOutputParser()
    result = chain.invoke({"content" : topic_content})
    return result


def generate_summary(topic, chunks ,llm):
    print(f"[INFO] Generating summary  :  {topic}")
    topic_content  = "\n".join([
        c.page_content
        for c in chunks
        if topic.lower()  in  c.page_content.lower()
        
    ])[:2000]
    
    if not topic_content :
        topic_content = "\n".join([
            c.page_content
            for c in chunks[:5]
        ])[:2000]
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Create a comprehensive study summary.

        Include:
        - Topic overview (2-3 sentences)
        - Key concepts (bullet list)
        - Important definitions
        - Exam tips
        - Quick revision points

        Make it easy to study from.
        Use clear headings.
        """),
        ("human", "Notes:\n{content}")
    ])
    
    chain  = prompt |  llm | StrOutputParser()
    result =  chain.invoke({"content" : topic_content})
    return result


def get_key_points(chunks,llm):
    print("[INFO] Extracting key points...")
    
    all_content = "\n".join([
        c.page_content for c in  chunks[:8]
    ])[:2000]
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Extract the most important key points
        from these study notes.

        Format:
        TOPIC: [Topic name]
        KEY POINTS:
        - [Point 1]
        - [Point 2]
        - [Point 3]

        EXAM TIPS:
        - [Tip 1]
        - [Tip 2]

        Separate each topic clearly.
        Focus on exam-worthy content.
        """),
        ("human", "Notes:\n{content}")
    ])
    chain = prompt | llm | StrOutputParser()
    result  =  chain.invoke({"content": all_content})
    return result 



