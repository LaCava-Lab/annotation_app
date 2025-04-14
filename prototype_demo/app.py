import streamlit as st
import pandas as pd
from pages import page2_execution


# Page navigation logic
def main(): 

    ##defaults in page configuration
    st.set_page_config(layout="wide")


    if "paper_data" not in st.session_state:
        df = pd.read_csv("Papers/selection.csv", header=0)
        df.fillna(value={'subtitle':'0'}, inplace=True)
        st.session_state["paper_data"] = df


    if "current_page" not in st.session_state:  
        st.session_state["current_page"] = "page2"

    # Navigation handler
    current_page = st.session_state["current_page"]
    if current_page == "page2":
        page2_execution.demo()


    #load cached @datasets
    #users
    # if "user_data" not in st.session_state:
    #     st.session_state["user_data"] = "read_USER_TABLE"
    #papers
    #saved_data
    #submitted_data

if __name__ == "__main__":
    main()

