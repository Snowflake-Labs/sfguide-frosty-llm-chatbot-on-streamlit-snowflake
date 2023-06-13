import streamlit as st
import re
from . import prompts
from .utils import llm_chat

# TODO: Update this app to actually run successfully, verify it with basic prompts
st.title("Frosty")

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]
conn = st.experimental_connection("snowpark")

def get_response(prompt):    
    st.session_state.messages.append({"role": "user", "content": prompt})
    # prompt engineering LLM to generate sql code
    st.session_state.messages.append(
        {
            "role": "user",
            "hide": True,
            "content": prompts.GEN_SQL.format(
                user_prompt=prompt,
            ),
        }
    )
    # Call LLM
    response = llm_chat(st.session_state.messages)
    sql = re.search(r"<sql>(.*)</sql>", response, re.DOTALL).group(1)
    # Execute the sql code
    results = conn.query(sql)
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "sql": sql, "results": results}
    )

user, assistant = st.chat_layout()
prompt = st.chat_input()
if prompt:
    get_response(prompt)
    
# display the chat messages   
for message in st.session_state.messages:
    if "hide" in message:
        continue
    if message["role"] == "user":
        user.write(message["content"])
    else:
        if "sql" in message:
            assistant.code(message["sql"], language="sql")
        if "results" in message:
            assistant.dataframe(message["results"])
        assistant.write(message["content"])
