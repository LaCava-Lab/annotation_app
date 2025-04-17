from text_highlighter import text_highlighter
import streamlit as st
import pandas as pd

#@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"] 
    if tab_name=="Front page":
        tmp = df[(df.section_title=="Title") | (df.section_title=="Authors") | (df.section_title=="Abstract")]
        return tmp['paragraph_string'].str.cat(sep="\n\n")
    elif tab_name in ["Introduction", "Materials and Methods", "Results", "Discussion", "Legends"]:
        txt = ""
        tmp=df[df.section_title==tab_name]
        # Get subtitles in their original order
        subsections = tmp['subtitle'].unique()  # Preserve order
        for sub in subsections:
            if sub=='0':
                tmp3 = tmp['paragraph_string'].str.cat(sep="\n\n")
                txt = txt + str(tmp3) + "\n\n" 
            else:
                if txt=="":
                    txt = txt + str(sub)
                else:
                    txt = txt + "\n\n" + str(sub)
                tmp2 = tmp[tmp.subtitle==sub]
                tmp3 = tmp2['paragraph_string'].str.cat(sep="\n")
                txt = txt + "\n\n" + str(tmp3)
        return txt
    else:
        return "Trouble"

@st.cache_data
def get_labels():
    return [("buffer", "pink" ), ("pH", "lightsalmon"), ("salt", "lightblue" ), ("detergent", "yellow" ), ( "chelating", "orange" ), ( "inhibitors", "violet" ),( "other", "lightgrey" )]


# Via sidebar
def demo():

    st.title("Data selection")
    st.link_button("Go to paper", 'https://doi.org/10.1073/pnas.1121568109')
    st.subheader("This is the actual annotation part!\n Please highlight the text as precicely as possible.\nYou will have a last opportunity to edit your data before you exit.")
    sidebar()

    names= ["Front page", "Introduction", "Materials and Methods", "Results", "Discussion", "Legends"]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(names)
    for n,t in zip(names, [ tab1, tab2, tab3, tab4, tab5, tab6]):
        with t:
            result = text_highlighter(
                text=get_tab_body(n),
                labels=get_labels(),
                # Optionally you can specify pre-existing annotations (eg for a user continuing a past session):
                #annotations=[],
                text_height=400)
            st.sidebar.write(result)
            

def sidebar():
    with st.sidebar:
        option_map = {
        0: "Co-IP",
        1: "Affinity purification",
        2: "X-ray crystallography",
        3: "NMR"
        }

        protocol = st.segmented_control("Select protocol", 
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single")

        st.write("Your selected option: ", f"{None if protocol is None else option_map[protocol]}")
        # st.write(result)

if __name__ == "__main__":
    demo()

