import streamlit as st
import openai

## Validate Snowflake connection ##

conn = st.experimental_connection("snowpark")
df = conn.query("select current_warehouse()")
st.write(df)

## Validate OpenAI connection ##
openai.api_key = st.secrets["OPENAI_API_KEY"]

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "What is Streamlit?"}
  ]
)

st.write(completion.choices[0].message.content)
