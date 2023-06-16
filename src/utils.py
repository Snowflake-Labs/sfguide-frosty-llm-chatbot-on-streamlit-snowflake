from typing import List, Dict
import openai
import streamlit as st


def llm_chat(chat_history: List[Dict]):
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": m["role"], "content": m["content"]} for m in chat_history],

    )
    return resp.choices[0].message.content


@st.cache_data()
def get_table_context(table_str: str):
    table = table_str.split(".")
    conn = st.experimental_connection("snowpark")
    columns = conn.query(
        f"SELECT COLUMN_NAME, DATA_TYPE FROM {table[0]}.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{table[1]}' AND TABLE_NAME = '{table[2]}'"
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
