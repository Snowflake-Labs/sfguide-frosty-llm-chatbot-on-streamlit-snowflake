from typing import List, Dict
import openai
import re
import streamlit as st

import prompts


conn = st.experimental_connection("snowpark")


def llm_chat(chat_history: List[Dict]):
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": m["role"], "content": m["content"]} for m in chat_history],

    )
    return resp.choices[0].message.content


@st.cache_data(show_spinner=False)
def get_table_context(table_str: str):
    table = table_str.split(".")
    columns = conn.query(
        f"SELECT COLUMN_NAME, DATA_TYPE FROM {table[0]}.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{table[1]}' AND TABLE_NAME = '{table[2]}'",
    )
    columns = "\n".join(
        [
            f"{columns['COLUMN_NAME'][i]}: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

Here are the columns of the {'.'.join(table)}

<columns>
{columns}
</columns>
    """
    return context


def get_response(prompt, table_context):
    # prompt engineering LLM to generate sql code
    st.session_state.messages.append(
        {
            "role": "system",
            "hide": True,
            "content": prompts.GEN_SQL.format(
                user_prompt=prompt,
                context=table_context,
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
    return message


def render_message(message):
    if "hide" in message:
        return
    if message["role"] == "user":
        st.chat_message("user", background=True).write(message["content"])
    else:
        assistant = st.chat_message("assistant")
        assistant.write(message["content"])
        if "sql" in message:
            assistant.code(message["sql"], language="sql")
        if "results" in message:
            assistant.dataframe(message["results"])
