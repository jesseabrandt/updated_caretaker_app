#streamlit app for summarizing data
import streamlit as st
import pandas as pd
import datetime
import template_summarize # import the template summarization function
from openai import OpenAI
#import set_environmental_variables

st.set_page_config(page_title= "Summarizer", page_icon="📊")

st.title("Summarizer")
selectors = st.container() # container for selectors
summary_space = st.container() # container for summary display
# load data
if "df" not in st.session_state:
    #st.session_state.df = pd.read_csv("data/full_dataset.csv")
    st.session_state.df = pd.DataFrame(columns = ["Description", "Category", "Created By", "Date", "Time"])
    st.session_state.df["Date"] = pd.to_datetime(st.session_state.df["Date"])
    st.session_state.df = st.session_state.df.drop_duplicates()
# if "sent_scores" not in st.session_state:
#     st.session_state.sent_scores = []

#numerical_data = pd.read_csv("data/numerical_data.csv")
# select date range
date_range = selectors.radio("Select date range for summarization:", 
    ("Today", "Past 7 days", "Past 30 days", "Custom range", "All")
)
if date_range == "Custom range":
    start_date = selectors.date_input("Start date")
    end_date = selectors.date_input("End date")
elif date_range == "Today":
    start_date = datetime.date.today()
    end_date = datetime.date.today()
elif date_range == "Past 7 days":
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=6)
elif date_range == "Past 30 days":
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=29)
elif date_range == "All":
    end_date = datetime.date.today()
    start_date = pd.Timestamp.min

# select summarization mode
selectors.write("At this time, summaries are limited to displaying the data, with sentiment analysis scores included in AI Summarization Mode.")
selectors.write("More advanced summary features fall under the scope of the other use case.")
mode = selectors.segmented_control(
    options = ["Template-based Summarization", "AI Summarization"],
    label = "Select summarization mode",
    selection_mode = "multi",
    default = "Template-based Summarization"
    )
client = OpenAI()
def generate_summary():
    #summary_space.write(("Start date: " + str(start_date) + ". End date: " + str(end_date) + ".")) # placeholder. will need to use session state here
    st.session_state.df["Date"] = pd.to_datetime(st.session_state.df["Date"])
    returned_data = template_summarize.generate_template_summary(start_date, end_date, st.session_state.df)
    #time.sleep(2)  # Simulate a delay for the spinner

    #summary_space.write(returned_data.info())
    #placeholder, showing that it returned the data
    
    if("AI Summarization" in mode):
        sent_scores = []
        descriptions = returned_data["Description"].tolist()
        for i in range(len(descriptions)):
            print(i)
            description = (descriptions[i])
            description = str(description)
            response = client.responses.create(
            prompt={
                "id": "pmpt_6873229872988194bf9fdd31875f1a8200fd63631840416f",
                "version": "2"
            },
            input=description,
            max_output_tokens=2048
            )
            sent_scores.append(response.output[0].content[0].text)
        returned_data["Sentiment Score"] = sent_scores
        returned_data["Sentiment Score"] = pd.to_numeric(returned_data["Sentiment Score"])

    summary_space.dataframe(returned_data)
    #st.session_state
    #numerical_data = pd.read_csv("data/numerical_data.csv")
    #text_data = pd.read_csv("data/text_data.csv")
    # how to store data best?
    #write summary code in separate file. Functions should take start and end date as arguments

selectors.button("Generate Summary", on_click = generate_summary)



