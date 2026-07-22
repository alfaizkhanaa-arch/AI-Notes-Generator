import  streamlit as st  
import  sys
import  os 

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from rag import(
    load_llm,
    load_embbedings,
    process_notes,
    generate_flashcards,
    generate_summary,
    genrate_quiz,
    bulid_qa_chain,
    get_key_points
)
from utiils import (
    display_study_card,
    display_flashcard,
    display_source,
    display_chat,
    parse_flashcard
    
)

#### Page Config
st.set_page_config(
     page_title = "Study Notes Assistant",
    page_icon  = "📚",
    layout     = "wide"
)
# Load Models
@st.cache_resource(show_spinner="Loading LLM ...")
def get_llm():
    llm =  load_llm()
    return llm 

@st.cache_resource(show_spinner="Loading Embeddings")
def get_embeddings():
    embeddings = load_embbedings()
    return embeddings

llm =  get_llm()
embeddings =  get_embeddings()

## Session State 
defaults  = {
    "messages" : [],
    "qa_chain":  None,
    "retriever": None,
    "chunks":  None,
    "processed" :False,
    "doc_names" : [],
    "quiz": None,
    "flashcards" :None,
    "summary": None,
    "key_points" :None
    
    
}
for key , value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] =  value

# Title
# ─────────────────────────────────────
st.title("📚 Study Notes Assistant")
st.write("Upload study notes and study smarter!")
st.divider()


with st.sidebar:
    st.title("🗃️ Uplaoded Study Note")
    st.write("👁️‍🗨️Supported PDF , TXT")
    st.divider()
    
    uploaded_files =  st.file_uploader(
        "Choose notes files",
        type = ["pdf","txt"],
        accept_multiple_files= True
    )
    if uploaded_files:
        st.write("Selected file:")
        for f in uploaded_files:
            st.write(f"-{f.name}")
        if st.button(
            "Process Note:",
            type = "primary",
            use_container_width= True
        ):
            with st.spinner("Processing notes..."):
                try :
                    vectorstore,chunks =  process_notes(
                        uploaded_files,
                        embeddings
                    )
                    chain,retriever =  bulid_qa_chain(
                        vectorstore,
                        llm
                    )
                    st.session_state.qa_chain =  chain
                    st.session_state.retriever =  retriever
                    st.session_state.chunks =  chunks
                    st.session_state.doc_names =  [
                        f.name for f in uploaded_files
                    ]
                    st.session_state.processed =  True
                    st.session_state.message = []
                    
                    st.success(
                        f"Done ! {len(chunks)} chunks!"
                    )
                except ValueError as e :
                    st.error(str(e))
                except Exception as  e :
                    st.error(f"Error : {str(e)}")
        st.divider()
        
        if st.session_state.processed :
            st.subheader("Stats")
            st.metric("Chunks",len(st.session_state.chunks))
            st.metric("Files",len(st.session_state.doc_names))
            
            st.write("Loaded Files : ")
            for name in st.session_state.doc_names:
                st.write(f" - {name}")
        if st.button("Clear All", use_container_width= True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()
        if st.session_state.processed :
            st.success("Ready to study !")
        else:
            st.warning("Upload notes first")
            
            
            
### Main Area 
if not st.session_state.processed :
    st.info("🛅 Uploaded study notes from sidebar!")
    col1,col2 ,col3 =  st.columns(3)
    with col1 :
        st.markdown("""
                    ### 📂 Step 1
                        Uploaded your 
                        study notes
                        PDF or TXT
                    """)
    with col2 : 
        st.markdown("""
                    ### 👆 Step 2
                         Click Process 
                         Notes and wait
                
                    """)
    with col3 :
        st.markdown("""
                    ### 📚 Step 3
                        Study smarter
                        with AI help
                    
                    """)    
    st.divider()
    st.header("🤔 What You Can Do :   ")
    features = [
        "Ask questions about your notes",
        "Generate quiz questions",
        "Create flashcards",
        "Get topic summaries",
        "Extract key points",
        "Get exam tips"   
    ]
    for f in features :
        st.write(f"👉 {f}")

else :
    ## tabs 
    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "Ask Questions",
        "Generate Quiz",
        "Flashcards",
        "Topic Summary",
        "Key Points"
    ])
    with tab1 :
        st.subheader("Ask About You Note")
        st.write("Quick Question ")
        quick = [
            "What is Python?",
            "Explain Machine Learning",
            "What is a Stack?",
            "Types of ML?",
            "What is Binary Tree?"
        ]   
        cols =  st.columns(len(quick))
        for i,q in enumerate(quick):
            with cols[i]:
                if st.button(
                    q,
                    key =  f"q_{i}"
                ):
                    with st.spinner("Searching..."):
                        try:
                            docs =  st.session_state.retriever.invoke(q)
                            answer =  st.session_state.qa_chain.invoke(q)
                            st.session_state.messages.append({
                                "role" : "human",
                                "content" : q
                            })              
                            st.session_state.messages.append({
                                "role" : "ai",
                                "content":  answer
                            })
                            st.rerun()
                        except Exception as e :
                            st.error(f"Error : {str(e)}")
        st.divider()
        display_chat(st.session_state.messages)
        
        if prompt := st.chat_input(
            "Ask about your notes..."
        ):
            with st.chat_message("human"):
                st.write(prompt)
                
            st.session_state.messages.append({
                "role" : "human",
                "content" :prompt
            })
            with st.chat_message("ai"):
                with st.spinner("Thinking..."):
                    try:
                        docs = (
                            st.session_state.retriever.invoke(prompt)
                        )
                        answer = st.session_state.qa_chain.invoke(prompt)
                        
                        display_study_card(
                            answer,
                            color = '#4CAF50'
                        )
                        display_source(docs)
                    except Exception as e :
                        st.error(f"Error : {str(e)}")
                st.session_state.messages.append({
                    "role" : "ai",
                    "content" : answer
                })
## Tab 2 : Genreate a quiz 
    with tab2:
        st.subheader("Generate Quiz")
        st.write("Test your knowleadge")
        col1,col2 =  st.columns(2)
    
        with col1 :
            topic  =  st.text_input(
            "Enter topic :  ",
            placeholder="Python, Machine Learning..."
        )         
        
        with col2  :  
         num_q =  st.slider(
            "Number of question",
            min_value = 3,
            max_value= 10,
            value=5
        )  
        if st.button(
        "Generate Quiz ",
        use_container_width= True,
        type  =  "primary",
        disabled =  not topic
    ):
            with st.spinner("Creating quiz..."):
                try:
                  quiz  =  genrate_quiz(
                    topic,
                    st.session_state.chunks,
                    llm,
                    num_q
                )
                  st.session_state.quiz =  quiz
                except Exception as e :
                    st.error(f"Error : {str(e)}")
    if st.session_state.quiz:
        st.divider()
        st.subheader("Your Quiz :")
        display_study_card(
            st.session_state.quiz,
            color = "#2196F3"
        )
        col1,col2 =  st.columns(2)
        with col1 :
            if st.button(
                "Generate New Quiz ",
                use_container_width= True
            ):
                st.session_state.quiz = None
                st.rerun()
                
                
#### Tab 3  : Flashcard
    with tab3 :
        st.subheader("Study Flashcard")
        st.write("Flip through key concepts!")
        
        topic_flash =  st.text_input(
            "Enter topic for flashcard: ",
            placeholder="Python, Data Structures...",
                key="flash_topic"
        )       
        if st.button(
            "Generate Flashcards",
                use_container_width = True,
                type                = "primary",
                disabled            = not topic_flash
        ):
            with st.spinner("Creating Flashcards...."):
                try :
                    flashcards =  generate_flashcards(
                        topic_flash,
                        st.session_state.chunks,
                        llm
                    )
                    st.session_state.flashcards = flashcards
                except Exception as e :
                    st.error(f"Error : {str(e)}")
        if st.session_state.flashcards:
            st.divider()
            st.subheader("Your Flashcards :")
            cards = parse_flashcard(
                st.session_state.flashcards
                
            )
            if cards :
                for  i ,card in enumerate(cards):
                    display_flashcard(
                        card["front"],
                        card["back"],
                        i+1
                    )
            else:
                display_study_card(
                    st.session_state.flashcards,
                    color = '#FF9800'
                )
    # Tab - 4  : Topic Summary
    with tab4 :
        st.subheader("Topic Summary")
        st.write("Get a quick summary of any topic!")
        
        topic_sum = st.text_input(
            "Enter topic to summarize",
            placeholder="Python, Machine Learning...",
            key="sum_topic"
            
        )
        if st.button(
                "Generate Summary",
                use_container_width = True,
                type                = "primary",
                disabled            = not topic_sum
            ):
            with st.spinner("Generating summary"): 
                try : 
                    summary = generate_summary(
                        topic_sum,
                        st.session_state.chunks,
                        llm
                    )
                    st.session_state.summary  = summary
                except Exception as e :
                    st.error(f"Error :  {str(e)}")
        if st.session_state.summary:
            st.divider()
            st.subheader("Summary:")
            display_study_card(
                st.session_state.summary,
                color =  "#9C27B0"
            )                 
            st.download_button(
                "Download Summary ",
                st.session_state.summary,
                file_name= "study_summary.txt",
                mime = "text/plain",
                use_container_width= True
            )
            
### Tab 5 : Key Points
    with tab5:
        st.subheader("Key Points & Exam Tips")
        st.write("Most important points from all notes!")

        if st.button(
            "Extract Key Points",
            use_container_width=True,
            type="primary"
        ):
            with st.spinner("Extracting key points..."):
                try:
                    # Generate key points
                    st.session_state.key_points = get_key_points(
                        st.session_state.chunks,
                        llm
                    )

                    if st.session_state.key_points:
                        st.divider()
                        st.subheader("Key Points")

                        display_study_card(
                            st.session_state.key_points,
                            color="#F44336"
                        )

                        st.download_button(
                            "Download Key Points",
                            st.session_state.key_points,
                            file_name="key_points.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Error: {e}")