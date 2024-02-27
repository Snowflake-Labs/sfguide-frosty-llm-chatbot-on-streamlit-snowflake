import streamlit as st
import streamlit.components.v1 as components
import pygwalker as pyg

st.set_page_config(
    page_title="Data Visualizer",
    page_icon="📊",
    layout="wide"
)

st.write("# 📊 Welcome to the TEx Visualizer! ")

# Launch pygwalker UI
def launchPyg():
    
    #initialize df
    df = None
    
    # create dataframe  
    for message in st.session_state.messages:
        if "results" in message:
            df = message["results"]
    if df is None:
        conn = st.connection("snowflake")
        df = conn.query("select * from EO_DATA.PUBLIC.EO_LAST_REPORTED")

    # Generate the HTML using Pygwalker
    pyg_html = pyg.to_html(df)
    
    # Embed the HTML into the Streamlit app
    components.html(pyg_html, height=1000, scrolling=True)


launchPyg()


# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )