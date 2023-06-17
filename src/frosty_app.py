import openai
import re
import streamlit as st
from prompts import get_system_prompt

st.title("☃️ Frosty")

system_prompt = get_system_prompt()

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "system", "content": system_prompt, "hide": True},
        {"role": "assistant", "content": "How can I help?"}
    ]

# Get user input and LLM response
prompt = st.chat_input()
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        #engine="gpt-4",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
    )

    # Parse the response for a SQL query
    message = {"role": "assistant", "content": response.choices[0].message.content}
    sql_match = re.search(r"```sql\n(.*)\n```", message["content"], re.DOTALL)
    if sql_match:
        # Execute and save the SQL query if available
        sql = sql_match.group(1)
        message["sql"] = sql
        conn = st.experimental_connection("snowpark")
        message["results"] = conn.query(sql)
    
    # Save the result
    st.session_state.messages.append(message)

# display the chat messages   
for message in st.session_state.messages:
    if "hide" in message:
        continue
    if message["role"] == "user":
        st.chat_message("user", background=True).write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
            if "results" in message:
                st.divider()
                st.dataframe(message["results"])
