import streamlit as st
def display_study_card(content,color = "#4CAF50"):
    st.markdown(
        f"""
            <div style = "
            background-color : #f8f9fa;
            padding          : 1.5rem;
            border-radius    : 0.5rem;
            border-left      : 4px solid {color};
            margin-bottom    : 1rem;
            "
            >
        {content.replace(chr(10),'<br>')}
        
        """, 
        unsafe_allow_html= True
        
    )
def display_flashcard(front,back,index):
    with st.expander(f"Card : {index} : {front}"):
        st.success(f"Answer :{back}")
        
def display_source(docs):
        if not docs :
            return 
        with st.expander("View Source Notes "):
            for i , doc in enumerate(docs):
                col1 , col2 = st.columns([1,4])
                with col1 : 
                    st.metric(
                        f"Source {i + 1}",
                        doc.metadata.get("source","N/A")
                    )
                with col2 : 
                    st.write(
                        doc.page_content[:300] + "..."
                    )
                st.divider()

def display_chat(messages):
    for msg in messages :
        with st.chat_message(msg['role']):
            st.write(msg['content'])
            

def parse_flashcard(flashcard_text):
    
    cards = []
    lines = flashcard_text.split("\n")
    front = ""
    back = ""
    for line in lines :
        line =  line.strip()
        if line.startswith("Front:"):
            front =  line.replace("Front:", "").strip()
        elif line.startswith("Back:"):
            back =  line.replace("Back:","").strip()
            if front and back :
                cards.append(
                    {
                    "front":  front,
                    "back":  back
                })
                front = ""
                back  = ""
    return cards            