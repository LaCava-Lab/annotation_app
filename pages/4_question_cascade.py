import streamlit as st

st.set_page_config(page_title="Questionnaire", layout="wide")

paper_title = "Authors2, Title2, Journal2, Issue2, volume2, pages2"
full_text_url = "https://example.com/fulltext/2"

spacer_left, main_col, spacer_right = st.columns([1, 2, 1])
with main_col:
    st.markdown("### You have selected to annotate the paper:")
    st.markdown(f"**{paper_title}**\n\n"
                "Use the link below to scan through the full-text paper and then answer the quick questionnaire. "
                "You can go back via “Pick another” as many times as you want. You’ll only be allowed to abandon a “Confirmed Paper” twice. "
                "Once you’re happy, press “Confirm paper.”")

    st.markdown(
        f"""<a href="{full_text_url}" target="_blank">
                <button style="
                  padding:8px 16px;
                  background-color:#5A9;
                  color:white;
                  border:none;
                  border-radius:4px;
                  cursor:pointer;
                ">
                  Go to full-text paper
                </button>
            </a>""",
        unsafe_allow_html=True,
    )

    st.write("---")

    # Q1: Yes/No
    q1 = st.radio(
        "1. Is the paper describing wet lab experiments that aim to understand protein interactions?",
        ("Yes", "No"),
        index=1,
        key="q1"
    )
    disabled = (q1 == "No")

    # 1a–c
    st.markdown("**1a.** What is the main method the authors use to understand protein interactions?")
    st.text_input(
    label="Answer 1a (hidden)", 
    placeholder="Type your answer here…",
    disabled=disabled, 
    key="q1a",
    label_visibility="collapsed",)

    st.markdown("**1b.** Is this method preserving protein interactions in a cell-free system (eg whole cell extracts)?")
    st.radio(
    label="Answer 1b (hidden)", 
    options=("Yes","No"),
    disabled=disabled,
    key="q1b",
    label_visibility="collapsed",)

    st.markdown("**1c.** Is this method using any type of cross-linking to preserve protein interactions?")
    st.radio(
    label="Answer 1c (hidden)", 
    options=("Yes","No"), 
    disabled=disabled, 
    key="q1c", 
    label_visibility="collapsed")

    # Q2 & Q3
    levels = ["Basic", "MSc course", "MSc research", "PhD field", "PhD research", "Expert"]

    st.selectbox(
    "2. What is your level of familiarity with the topic of this paper?",
    levels,
    key="q2",
    disabled=disabled)

    st.selectbox(
    "3. What is your level of familiarity with the methods and experiments in this paper?",
    levels,
    key="q3",
    disabled=disabled)



    st.write("")

    sp1, btn_col1, gap, btn_col2, sp2 = st.columns([1, 2, 1.5, 2, 1])
    with btn_col1:
        if st.button("Pick another"):
            st.switch_page("pages/2_pick_paper.py")
    with btn_col2:
        if st.button("Confirm paper", type="primary", disabled=disabled):
            st.switch_page("pages/5_detail_picker.py")
