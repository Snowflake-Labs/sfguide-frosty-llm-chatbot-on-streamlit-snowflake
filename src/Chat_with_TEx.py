from openai import OpenAI
import pygwalker as pyg
import re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from prompts import get_system_prompt
from streamlit_pills import pills


st.set_page_config(page_title="Chat with TEx", page_icon="👋", layout="wide")
# st.sidebar.header("👋 Chat with Tex")

st.title("Chat with TEx 👋")
st.markdown("##### Your friendly neighborhood TK E&O assistant")

# Initialize the chat messages history
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
if "messages" not in st.session_state:
    # system prompt includes table information, rules, and prompts the LLM to produce
    # a welcome message to the user.
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

    
# lst_suggest = ["What is the BOH $ by ODM and Month", "Show me the total excess by BU and Month"]
# st.session_state.messages.append({"role": "assistant", "content": pills("Example prompts:",lst_suggest) }) 

# Prompt for user input and save
if prompt := st.chat_input():   
    st.session_state.messages.append({"role": "user", "content": prompt})
    # suggested_prompt_selected = pills("Example prompts:", st.session_state.suggested_prompts) 

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":        
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])
        # if "suggested_prompts" in message:
        #     # st.session_state.suggested_prompts = ["Show me the total excess by BU and Month", "What is the BOH $ by ODM and Month"]        
        #     suggested_prompt_selected = pills("Example prompts:", lst_suggest) 
    

# If last message is not from assistant, we need to generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = ""
        resp_container = st.empty()
        for delta in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
            response += (delta.choices[0].delta.content or "")
            resp_container.markdown(response)

        message = {"role": "assistant", "content": response}
        # Parse the response for a SQL query and execute if available
        sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1)
            conn = st.connection("snowflake")
            message["results"] = conn.query(sql)
            st.dataframe(message["results"])                               
        st.session_state.messages.append(message)


