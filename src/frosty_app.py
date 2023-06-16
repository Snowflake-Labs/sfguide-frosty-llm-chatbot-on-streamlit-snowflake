import streamlit as st
import re
import prompts
from utils import llm_chat, get_table_context

st.title("Frosty")

_QUALIFIED_TABLE_NAME = "FROSTY_SAMPLE.CYBERSYN_SEC.SEC_REPORT_TEXT_LINKED"

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]
conn = st.experimental_connection("snowpark")

def get_response(prompt):    
    st.session_state.messages.append({"role": "user", "content": prompt})
    # prompt engineering LLM to generate sql code
    st.session_state.messages.append(
        {
            "role": "system",
            "hide": True,
            "content": prompts.GEN_SQL.format(
                user_prompt=prompt,
                context=get_table_context(_QUALIFIED_TABLE_NAME),
            ),
        }
    )
    # Call LLM
    response = llm_chat(st.session_state.messages)
    message = {"role": "assistant", "content": response}
    sql_match = re.search(r"<sql>(.*)</sql>", response, re.DOTALL)
    if sql_match:
        sql = sql_match.group(1)
        message["sql"] = sql
        # Execute the sql code
        message["results"] = conn.query(sql)
    st.session_state.messages.append(message)

# user, assistant = st.chat_layout()
# prompt = st.chat_input()
prompt = st.text_input("Prompt:")
user, assistant = st.tabs(["User", "Assistant"])
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
