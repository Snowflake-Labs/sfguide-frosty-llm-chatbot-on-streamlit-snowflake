import streamlit as st
import streamlit_pills as stp

# Initialize session state variables
if "suggestions_list" not in st.session_state:
    st.session_state.suggestions_list = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
if "suggestions_icons" not in st.session_state:
    st.session_state.suggestions_icons = ["🔍", "💡", "📝"]
if "pills_index" not in st.session_state:
    st.session_state.pills_index = None

# Display the pills
predefined_prompt_selected = stp.pills("Query suggestions:", st.session_state.suggestions_list, st.session_state.suggestions_icons, index=st.session_state.pills_index)

# If a pill is selected, remove it from the list and reset the pills
if predefined_prompt_selected:
    index_to_eliminate = st.session_state.suggestions_list.index(predefined_prompt_selected)
    st.session_state.suggestions_list.pop(index_to_eliminate)
    st.session_state.suggestions_icons.pop(index_to_eliminate)
