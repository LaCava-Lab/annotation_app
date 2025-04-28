import streamlit as st
from st_components.TableSelect import TableSelect
from st_components.Cmp_Template import MyComponentName

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 370px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Using "with" notation
with st.sidebar:
    st.title("Paper Annotation")

    data = [
        {"Experiment name": "Immunoprecipitation", "Type": "PI"},
        {"Experiment name": "MS screen", "Type": "non-PI"},
    ]

    # Create a list of options (e.g., "0", "1" representing index)
    options = list(range(len(data)))

    # Show the table header
    st.markdown("**Experiment name — Type**")
    selected_experiment = None

    # Draw the rows as single buttons
    for i, row in enumerate(data):
        label = f"{row['Experiment name']} — {row['Type']}"
        if st.button(label, key=f"type_button_{i}", use_container_width=True):
            if row['Type'] == "PI":
                selected_experiment = data[0]
                print(selected_experiment)
            else:
                selected_experiment = data[1]
                print(selected_experiment)

    TableSelect("something")
    MyComponentName()


