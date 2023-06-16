import streamlit as st
from utils import get_table_context, get_response, render_message

st.title("Frosty")

_QUALIFIED_TABLE_NAME = "FROSTY_SAMPLE.CYBERSYN_SEC.SEC_REPORT_TEXT_LINKED"
table_context = get_table_context(_QUALIFIED_TABLE_NAME)

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]

# display the existing chat messages   
for message in st.session_state.messages:
    render_message(message)

# Get and render user input
prompt = st.chat_input()
if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    # Get and render LLM response
    response = get_response(prompt, table_context)
    render_message(response)
    st.session_state.messages.append(response)
