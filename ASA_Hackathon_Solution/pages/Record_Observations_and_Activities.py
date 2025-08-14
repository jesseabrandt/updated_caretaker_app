# to run, once you have installed the packages, run the following command in the terminal:
# streamlit run dashboard.py
import streamlit as st #streamlit for web app
from openai import OpenAI
#import set_environmental_variables # This file should set the environment variables for OpenAI API key (see google doc)
#set environmental variable for api key somewhere else (docker image?)
#actually the api interactions should be in the backend
import pandas as pd
import numpy as np
import datetime
import re

st.set_page_config(page_title = "Record Observations and Activities", page_icon = ":memo:")

top = st.container() # container for the top part of the app interface (audio input, transcription, and classification button)

def new_recording(): 
    st.session_state.new_recording = True


client = OpenAI()

#SESSION STATE VARIABLES SHOULD BE replaced with a database or other persistent storage 

# initialize session state variable new_recording. 
# new_recording must be true to transcribe audio and classify sentences
# Much of this code should probably be moved to a function in a separate file
if "new_recording" not in st.session_state:
    st.session_state.new_recording = True
if "response_list" not in st.session_state:
    st.session_state.response_list = pd.DataFrame(columns = ["Description", "Category"])
if "previous_file" not in st.session_state:
    st.session_state.previous_file = "" # This will be used to save the previous file name if the user chooses to save and continue editing
if "username" not in st.session_state:
    st.session_state.username = "Default_User" # Default username, username could be provided before running app
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns = ["Description", "Category", "Created By", "Date", "Time"]) # DataFrame to store observations and activities
if "reset_df" not in st.session_state:
    st.session_state.reset_df = True
if "obs_date" not in st.session_state:
    st.session_state.obs_date = datetime.datetime.now()
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "switch_page" not in st.session_state:
    st.session_state.switch_page = False
if "reset" not in st.session_state:
    st.session_state.reset = False
#username
st.session_state.username = top.text_input("Username:", st.session_state.username)
st.session_state.obs_date = (top.date_input("Date of Observations/Activities"))
st.session_state.obs_date = datetime.datetime.combine(st.session_state.obs_date, datetime.time(0,0,0))
audio_value = top.audio_input("Record a voice message (up to two minutes)", on_change= new_recording)#recording widget

# function to classify sentences using openai
# can be moved to different file possibly
def classify_sentences():
    # Split the transcription into sentences
    sentences = re.split(string = st.session_state.transcript, pattern = "[.?!]")  # Split the transcription into sentences
    for i, sentence in enumerate(sentences):
        sentences[i] = sentence.strip()
        if(len(sentence) > 0 and sentence[-1] != "."):
            sentences[i] += "."
    
    
    st.session_state.new_recording = False
    st.session_state.response_list = []
    for sentence in sentences:
        if len(sentence )> 0:    
            # st.write(sentence, "is a sentence")
            st.session_state.response = client.responses.create(
            prompt={
                "id": "pmpt_686ada65dc448190b8e52891791bcad2041f63c0533aad72",
                "version": "5"
            },
            input = sentence
            )
            # st.write(st.session_state.response.output[0].content[0].text)
            row_data = {
                "Description": sentence,
                "Category": st.session_state.response.output[0].content[0].text
            }
            st.session_state.response_list.append(row_data)

if audio_value:
    #display audio player
    top.audio(audio_value)
    # Transcribe the audio if a new recording is made
    # TODO: prompt user to save previous transcription
    
    if st.session_state.new_recording:
        new_text = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_value
        )
        if "transcript" in st.session_state:
            st.session_state.transcript = st.session_state.transcript + " " + new_text.text
        else:
            st.session_state.transcript = new_text.text
        st.session_state.new_recording = False
    #editable transcription text area
    
st.session_state.transcript = top.text_area("Transcription:", st.session_state.transcript)
top.button("Classify", on_click=classify_sentences)#classification button - rename to something more intuitive?

    


response_df = pd.DataFrame(st.session_state.response_list)
# Display the responses in an editable table (can be deleted later)
#response_df = st.data_editor(response_df)

# Display the responses in a badge format with toggle buttons for reclassification
# (todo: combine with the editable table above)
classification_container = st.container()

#note: columns are responsive, which causes issues with mobile layout/any thin screen
containers = []
toggles = []
important_toggles = []
row_list = []

for i in range(len(response_df)):
    containers.append(classification_container.container())
    col1, col2, col3, col4 = containers[i].columns(4)#create four columns for each row
    row_list.append([col1,col2,col3,col4])
    toggles.append(col3.toggle("Reclassify", key = f"Reclassify_{i}" + response_df["Description"][i]))
    important_toggles.append(col4.toggle("Important", key = (f"Important_{i}" + response_df["Description"][i])))

#Reclassify sentences based on toggles
def reclassify_type(toggle, type):
    for i in range(len(toggle)):
        if toggle[i]:
            if type[i] == "Observation":
                type[i] = "Activity"
            elif type[i] == "Activity":
                type[i] = "Observation"
            else:
                type[i] = "Observation" #Default to Observation if output is something else
        elif type[i] != "Observation" and type[i] != "Activity":
            type[i] = "Activity" 
    return type   

def check_importance(toggle):
    important = ["No"] * len(toggle)
    for i in range(len(toggle)):
        if toggle[i]:
            important[i] = "Yes"
    return important

response_df["reclassify"] = toggles
response_df["Category"] = reclassify_type(response_df["reclassify"], response_df["Category"])
response_df["Is Important"] = check_importance(important_toggles)

if st.session_state.reset_df:            
    response_df["Created By"] = st.session_state.username
    response_df["Date"] = st.session_state.obs_date.strftime("%Y-%m-%d %H:%M:%S")
    response_df["Time"] = datetime.datetime.now().strftime("%H:%M:%S")
    response_df["Datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reset_df = False

for i in range(len(response_df)):
    if response_df["Category"][i] == "Observation":
        row_list[i][0].badge(response_df["Description"][i], color = "blue")
        row_list[i][1].badge(response_df["Category"][i], color = "blue")
    elif response_df["Category"][i] == "Activity":   
        row_list[i][0].badge(response_df["Description"][i], color = "green")
        row_list[i][1].badge(response_df["Category"][i], color = "green")

#should save to database

bottom = st.container()

def save_entries():
    st.session_state.df = pd.concat([st.session_state.df, response_df])
    st.session_state.df = st.session_state.df.drop_duplicates()
    #bottom.write("Entries saved to file.")
    #filename = "data/journal/journal_" + st.session_state.username + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    #bottom.write("filename: " + filename)
    #response_df.to_csv(filename)

    #return(filename)

def save_and_clear():
    st.session_state.transcript = ""
    save_entries()
    

def save_and_exit():
    save_entries()
    #go back to home page (in development)
    st.session_state.switch_page = True
    
def save_and_continue():
    #st.session_state.previous_file = 
    save_entries()
    #TODO: 
    st.session_state.reset = True


#st.write(response_df)
@st.dialog("Save all entries?")
def ask_whether_clear():
    st.write("Prototype version will save to session state. Download csv from table to save locally.")
    c1,c2,c3 = st.columns(3)
   #c1.button("Save and Exit to Main Menu", on_click=save_and_exit)
    c1.button("Save and Continue", on_click=save_and_continue)
    c2.button("Save and Exit", on_click = save_and_exit)
    c3.button("Cancel")
    st.rerun()#should be removed and replaced with ?

if st.session_state.reset:
    st.session_state.reset = False
    st.session_state.transcript = ""
    st.rerun()
if st.session_state.switch_page:
    st.session_state.switch_page = False
    st.session_state.transcript = ""
    st.switch_page("Home_Page.py")
bottom.button("Save Entries", on_click=ask_whether_clear)

st.session_state.df = bottom.data_editor(data = st.session_state.df, num_rows = "dynamic",
                                         column_order = ["Date", "Description", "Is Important", "Time", "Category", "Created By"])

