from typing import List, Dict
import streamlit as st

# TODO: Add the real working LLM code
def llm_chat(chat_history: List[Dict]):
    c = llm_client(st.secrets.API_KEY)
    
    resp = c.llm_response(prompt)
    return resp
