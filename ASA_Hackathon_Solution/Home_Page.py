import streamlit as st

st.set_page_config(page_title="Home Page", page_icon=":house:", layout="wide")

st.title("Caregiver Dashboard")

if "username" not in st.session_state:
    st.session_state.username = "Default_User" # Default username, username could be provided before running app

st.session_state.username = st.text_input("Username:", st.session_state.username)

st.write("Warning: This is a PROTOTYPE. Data entered here will be lost when the app is closed.")

#st.page_link(page = "Home_Page.py", label="Home Page")
st.header("What do you want to do?")
st.page_link(page = "pages/Record_Observations_and_Activities.py", label ="Record Observations and Activities",
             icon = "📝")
st.page_link(page = "pages/Summarizer.py", icon = "📊")