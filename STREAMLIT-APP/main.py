import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import requests as request
load_dotenv()

st.title("Groq ChatBot")
#initalizing Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Chat Input
if prompt := st.chat_input("Type your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Groq is thinking..."):
            response = request.post("http://localhost:8000/generate",
                                    json={"message": prompt})
            result = response.json()
            st.markdown(result["message"])
        st.session_state.messages.append({"role": "assistant", "content": result["message"]})
        
   # # when application response is text
    #  : Refer Streaming.py in FastAPI Demo
    #st.write(response.text) 
    
      # # when application response is Json
    #  : Refer myapp.py in FastAPI Demo
    result = response.json()
    #st.write(result["message"])
