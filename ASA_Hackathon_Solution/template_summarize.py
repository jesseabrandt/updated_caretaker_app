import pandas as pd
from datetime import datetime

#placeholders, will use input values from streamlit app
#start_date = datetime.strptime("2024-01-01", "%Y-%m-%d").date()
#end_date = datetime.strptime("2024-01-31", "%Y-%m-%d").date()

#may be best to load data in the streamlit app and pass it to this function
#and keep in session state

def generate_template_summary(start_date, end_date, data):
    print(start_date, end_date)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    data["Date"] = pd.to_datetime(data["Date"])
    print(data.info())
    filtered_data = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]
    return filtered_data
#generate_template_summary(start_date, end_date, numerical_data, text_data)



