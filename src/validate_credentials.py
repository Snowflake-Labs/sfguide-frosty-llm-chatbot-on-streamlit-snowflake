import streamlit as st
from openai import OpenAI

## Validate Snowflake connection ##

conn = st.connection("snowflake")
df = conn.query("select current_warehouse()")
st.write(df)

## Validate OpenAI connection ##
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "What is Streamlit?"}
  ]
)

st.write(completion.choices[0].message.content)
