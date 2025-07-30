import uuid
import pandas as pd
import streamlit as st
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
from src.database import save_annotations_to_db
from process_interchange import detail_picker


class Subpage:
    def __init__(self, index, label, doi_link, paper_data, sidebar_content, selections, highlighter_labels,
                 coffee_break, coffee_break_display):
        self.index = index
        self.label = label
        self.doi_link = doi_link
        self.sidebar_content = sidebar_content
        self.coffee_break = coffee_break
        self.coffee_break_display = coffee_break_display
        self.paper_data = paper_data
        self.highlighter_labels = highlighter_labels
        self.selections = selections
        self.prev_page_context = None
        self.experiments = []
        self.tabs = []
        self.coffee_break_1_saved = None
        self.coffee_break_2_saved = None
        self.coffee_break_3_saved = None

    def saveCoffeeBreak(self):
        index = self.index - 1

        if self.index == 2:
            for experiment in self.coffee_break_1_saved.to_dict(orient='records'):
                section = st.session_state.subpages[index]["experiments"][experiment["section"]]
                for i,nested_exp in enumerate(section):
                    if nested_exp["absolute_index"] == experiment["absolute_index"]:
                        # st.session_state.subpages[index]["experiments"][experiment["section"]][i]["type"] = experiment["exp_type"]
                        if(experiment["alt_exp_name"] == ""):
                            st.session_state.subpages[index]["experiments"][experiment["section"]][i]["alt_exp_text"] = None
                        else:
                            st.session_state.subpages[index]["experiments"][experiment["section"]][i]["alt_exp_text"] = experiment["alt_exp_name"]

                        for j,solution_set in enumerate(nested_exp["solutions"]):
                            for k,solution in enumerate(solution_set):
                                # st.session_state.subpages[index]["experiments"][experiment["section"]][i]["solutions"][j][k]["type"] = experiment["sol_type"]
                                if solution["text"] == experiment["sol_name"]:
                                    if(experiment["alt_sol_name"] == ""):
                                        st.session_state.subpages[index]["experiments"][experiment["section"]][i]["solutions"][j][k]["alt_sol_text"] = None
                                    else:
                                        st.session_state.subpages[index]["experiments"][experiment["section"]][i]["solutions"][j][k]["alt_sol_text"] = experiment["alt_sol_name"]

            # st.rerun()
            # st.write(self.coffee_break_1_saved.to_dict(orient='records'))
            # st.write(st.session_state.subpages[index]["experiments"])
        elif self.index == 3:
            current_bait = self.coffee_break_2_saved["baits"].to_dict(orient='records')
            current_interactors = self.coffee_break_2_saved["interactors"].to_dict(orient='records')
            current_experiment = self.coffee_break_2_saved["experiment"]

            for i,experiment in enumerate(st.session_state.subpages[index]["experiments"]):
                if current_experiment["absolute_index"] == experiment["absolute_index"]:
                    for j,bait in enumerate(experiment["baits"]):
                        if current_bait[0]["uuid"] == bait["uuid"]:
                            #EDIT BAIT
                            st.session_state.subpages[index]["experiments"][i]["baits"][j]["alt_name"] = current_bait[0]["bait_alt_name"]
                            st.session_state.subpages[index]["experiments"][i]["baits"][j]["alt_tag"] = current_bait[0]["bait_alt_tag"]
                            st.session_state.subpages[index]["experiments"][i]["baits"][j]["alt_species"] = current_bait[0]["bait_alt_species"]

                            for interactor in current_interactors:
                                for k,bait_interactor in enumerate(bait["interactors"]):
                                    if interactor["uuid"] == bait_interactor["uuid"]:
                                        #EDIT INTERACTOR
                                        st.session_state.subpages[index]["experiments"][i]["baits"][j]["interactors"][k]["alt_name"] = interactor["interactor_alt_name"]
                                        st.session_state.subpages[index]["experiments"][i]["baits"][j]["interactors"][k]["alt_species"] = interactor["interactor_alt_species"]

            # st.write(current_experiment)
            # st.write(current_bait)
            # st.write(current_interactors)
            # st.write(st.session_state.subpages[index]["experiments"])
            # st.warning("second coffee save")
            # st.rerun()
        elif self.index == 4:
            experiment = self.coffee_break_3_saved["experiment"]
            solution = self.coffee_break_3_saved["solution"]
            altered_solution = self.coffee_break_3_saved["altered_solution"]

            for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
                if exp["text"] == experiment["text"]:
                    for j, sol in enumerate(exp["solutions"]):
                        if sol["text"] == solution["text"]:
                            st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j] = altered_solution

            # st.write(experiment)
            # st.write(solution)
            # st.write(altered_solution)
            st.write(st.session_state.subpages[index]["experiments"])
            st.warning("third coffee save")

    def format_bait_props(self, text):
        return f"({text})" if text else ""

    def assign_experiments(self, experiments):
        self.experiments = experiments

    def return_data(self):
        return ["a", "b"]

    def check_tag(self, tag):
        if 'non-PI' in tag:
            return "non-PI"
        else:
            return "PI"

    def sidebar_info(self):
        with st.sidebar:
            st.subheader(self.sidebar_content["subtitle"])
            st.markdown(self.sidebar_content["description"])
            if self.doi_link:
                st.link_button("Go to full-text paper", self.doi_link, use_container_width=True)
            else:
                st.markdown("""
                    <div style="background-color:#ffdddd; color:#a94442; padding:10px 15px; border-left:6px solid #f44336; border-radius:4px; margin-bottom:15px;">
                    ⚠️ DOI link not available for this paper.
                    </div>
                """, unsafe_allow_html=True)

    def sidebar_widget(self):
        with st.sidebar:
            if self.sidebar_content["widget"] == "CARDS":
                for tab_index, tab_results in enumerate(self.selections):
                    for i, item in enumerate(tab_results):
                        self.colored_card(
                            title=f"{item['tag']}",
                            subtitle=item['text'],
                            bg_color=item['color']
                        )
                return "PI"
            elif self.sidebar_content["widget"] == "CARDS_SELECT":
                header = {
                    "column_1": "Experiment > Solution",
                    "column_2": "Type"
                }
                flat_list_experiments = [{
                    **item,
                    "solutions": [{
                        **inner_item,
                        "background_color": "#6290C3" if self.check_tag(inner_item["tag"]) == "PI" else "#F25757",
                        "text_color": "white",
                        "alt_sol_text": None,
                    } for inner_sublist in item["solutions"] for inner_item in inner_sublist]
                } for sublist in self.experiments.values() for item in sublist]
                flat_list_solutions = [{
                    **item,
                    "background_color": "#6290C3" if self.check_tag(item["tag"]) == "PI" else "#F25757",
                    "text_color": "white",
                    "alt_sol_text": None,
                } for sublist in self.selections for item in sublist]

                current_tab = st.session_state.active_experiment_widget.get("section")
                current_index = st.session_state.active_experiment_widget.get("absolute_index")

                if current_tab is not None or current_index is not None:
                    for i, experiment in enumerate(
                            st.session_state.subpages[self.index - 1]["experiments"][current_tab]):
                        if experiment["absolute_index"] == current_index:
                            updated_selections = [
                                [{**d, "alt_sol_text": None, "type": self.check_tag(d["tag"])} for d in inner_list]
                                for inner_list in self.selections
                            ]
                            st.session_state.subpages[self.index - 1]["experiments"][current_tab][i][
                                "solutions"] = updated_selections

                st.session_state.active_experiment_widget = TableSelect(header, flat_list_experiments, 2,
                                                                        key=f"table_select_{self.label}_{len(flat_list_experiments)}")

                st.session_state.active_experiment_widget = {
                    **st.session_state.active_experiment_widget,
                    "solutions": flat_list_solutions
                }

                if st.session_state.active_experiment_widget.get("type") == "non-PI":
                    return "non-PI"
                else:
                    return "PI"
            elif self.sidebar_content["widget"] == "EXPERIMENT_DETAILS":
                experiment_names = [
                    exp["alt_exp_text"] if exp["alt_exp_text"] else exp["text"]
                    for exp in self.experiments
                    if exp["type"] == "PI" # Filtering only PI experiments
                ]
                experiment_name = st.selectbox("Experiment", experiment_names)
                add_option = st.radio("Add :", ["Bait", "Interactor(s)"], horizontal=True, label_visibility="collapsed")
                if add_option == "Bait":
                    select_type = None
                    select_control = None

                    st.subheader("Bait is:")
                    col4, col5 = st.columns(2)
                    with col4:
                        select_type = st.selectbox("Select Type", ["Protein", "RNA", "DNA", "RNA:DNA hybrid"],
                                                   key="bait_type_1")
                    with col5:
                        select_control = st.selectbox("Select Control", ["Negative", "Positive", "No"],
                                                      key="bait_type_2")

                    bait_info_type = st.radio("Bait has:",
                                              ["Select Bait name", "Select Bait tag", "Select Bait species"])
                    st.session_state.select_type = f"bait_{bait_info_type.strip().split()[-1]}"

                    flattened = [item for sublist in self.selections if sublist for item in sublist]
                    last_item = flattened[-1] if flattened else {}

                    if st.session_state.select_type.startswith("bait_name"):
                        st.session_state.current_bait["name"] = last_item
                    elif st.session_state.select_type.startswith("bait_tag"):
                        st.session_state.current_bait["tag"] = last_item
                    elif st.session_state.select_type.startswith("bait_species"):
                        st.session_state.current_bait["species"] = last_item

                    if st.session_state.current_bait["name"] != {}:
                        st.write(f"Name: {st.session_state.current_bait['name']['text']}")
                    if st.session_state.current_bait["tag"] != {}:
                        st.write(f"Tag: {st.session_state.current_bait['tag']['text']}")
                    if st.session_state.current_bait["species"] != {}:
                        st.write(f"Species: {st.session_state.current_bait['species']['text']}")

                    st.button("Add", on_click=lambda: self.experiment_details_baits(experiment_name, select_type,
                                                                                    select_control),
                              use_container_width=True)

                    df = None
                    for exp in self.experiments:
                        if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                            df = pd.DataFrame(exp["baits"]).drop(columns=["interactors"], errors="ignore")
                    if not df.empty:
                        st.data_editor(
                            df,
                            use_container_width=True,
                            column_config={
                                "type": st.column_config.TextColumn("Type",disabled=True),
                                "control": st.column_config.TextColumn("Control",disabled=True),
                                "name": st.column_config.TextColumn("Name",disabled=True),
                                "alt_name": st.column_config.TextColumn("Alt. Name",disabled=True),
                                "tag": st.column_config.TextColumn("Tag",disabled=True),
                                "alt_tag": st.column_config.TextColumn("Alt. Tag",disabled=True),
                                "species": st.column_config.TextColumn("Species",disabled=True),
                                "alt_species": st.column_config.TextColumn("Alt. Species",disabled=True),
                            },
                            column_order=("type", "control", "name", "alt_name", "tag", "alt_tag", "species", "alt_species"),
                            key="exp_editor_1")
                else:
                    for i, experiment in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
                        if experiment["text"] == experiment_name or experiment["alt_exp_text"] == experiment_name:
                            if len(st.session_state.subpages[self.index - 1]["experiments"][i]["baits"]) == 0:
                                st.warning("There are no baits for this experiment!")
                                return "PI"

                            else:
                                bait_names = [bait["alt_name"] if bait["alt_name"] else bait["name"] for bait in
                                              st.session_state.subpages[self.index - 1]["experiments"][i]["baits"]]
                                bait_name = st.selectbox("Bait", bait_names)
                                current_bait = []
                                for bait in st.session_state.subpages[self.index - 1]["experiments"][i]["baits"]:
                                    if bait["name"] == bait_name or bait["alt_name"] == bait_name:
                                        cleaned = {k: v for k, v in bait.items() if k != "interactors"}
                                        current_bait = [cleaned]
                                # st.table(current_bait)
                                st.data_editor(
                                    current_bait,
                                    use_container_width=True,
                                    column_config={
                                        "type": st.column_config.TextColumn("Type",disabled=True),
                                        "control": st.column_config.TextColumn("Control",disabled=True),
                                        "name": st.column_config.TextColumn("Name",disabled=True),
                                        "alt_name": st.column_config.TextColumn("Alt. Name",disabled=True),
                                        "tag": st.column_config.TextColumn("Tag",disabled=True),
                                        "alt_tag": st.column_config.TextColumn("Alt. Tag",disabled=True),
                                        "species": st.column_config.TextColumn("Species",disabled=True),
                                        "alt_species": st.column_config.TextColumn("Alt. Species",disabled=True),
                                    },
                                    column_order=("type", "control", "name", "alt_name", "tag", "alt_tag", "species", "alt_species"),
                                    key="exp_editor_2")
                                st.subheader("Interactor is:")
                                select_type = st.selectbox("Select Type", ["Protein", "RNA", "DNA", "RNA:DNA hybrid"],
                                                           key=f"{current_bait[0]['name']}")

                                interactor_info_type = st.radio("Interactor has:",
                                                                ["Select Interactor name", "Select Interactor species"])
                                st.session_state.select_type = f"interactor_{interactor_info_type.strip().split()[-1]}"

                                flattened = [item for sublist in self.selections if sublist for item in sublist]
                                last_item = flattened[-1] if flattened else {}

                                if st.session_state.select_type.startswith("interactor_name"):
                                    st.session_state.current_interactor["name"] = last_item
                                elif st.session_state.select_type.startswith("interactor_species"):
                                    st.session_state.current_interactor["species"] = last_item

                                if st.session_state.current_interactor["name"] != {}:
                                    st.write(f"Name: {st.session_state.current_interactor['name']['text']}")
                                if st.session_state.current_interactor["species"] != {}:
                                    st.write(f"Species: {st.session_state.current_interactor['species']['text']}")

                                st.button("Add", on_click=lambda: self.experiment_details_interactors(experiment_name,
                                                                                                      bait_name,
                                                                                                      select_type),
                                          use_container_width=True)

                                df = None
                                for exp in self.experiments:
                                    if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                                        for bait in exp["baits"]:
                                            if bait["name"] == bait_name or bait["alt_name"] == bait_name:
                                                df = pd.DataFrame(bait["interactors"])
                                if not df.empty:
                                    st.data_editor(
                                        df,
                                        use_container_width=True,
                                        column_config={
                                            "type": st.column_config.TextColumn("Type",disabled=True),
                                            "name": st.column_config.TextColumn("Name",disabled=True),
                                            "alt_name": st.column_config.TextColumn("Alt. Name",disabled=True),
                                            "species": st.column_config.TextColumn("Species",disabled=True),
                                            "alt_species": st.column_config.TextColumn("Alt. Species",disabled=True),
                                        },
                                        column_order=("type", "name", "alt_name", "species", "alt_species"),
                                        key="exp_editor_1")
                return "PI"
            elif self.sidebar_content["widget"] == "SOLUTION_DETAILS":
                experiment_names = [
                    exp["alt_exp_text"] if exp["alt_exp_text"] else exp["text"]
                    for exp in self.experiments
                    if exp["type"] == "PI" # Filtering only PI experiments
                ]
                experiment_name = None
                solution_names = []
                solution_name = None
                PH_old = ""
                temp_old = ""
                time_old = "0–5 min"
                composition_old = "Solution details not listed: reference paper"
                composition_chems = []

                col1, col2 = st.columns(2)
                with col1:
                    experiment_name = st.selectbox("Experiment", experiment_names)

                for exp in self.experiments:
                    if exp["text"] in experiment_name or exp["alt_exp_text"] in experiment_name:
                        solution_names = [
                            sol["alt_sol_text"] if sol["alt_sol_text"] else sol["text"]
                            for sol in exp["solutions"]
                            if sol["type"] == "PI"
                        ]
                        break

                with col2:
                    solution_name = st.selectbox("Solution", solution_names)

                for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
                    if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                        for j, sol in enumerate(exp["solutions"]):
                            if sol["text"] == solution_name or sol["alt_sol_text"] == solution_name:
                                PH_old = sol["details"]["ph"]
                                temp_old = sol["details"]["temp"]
                                time_old = sol["details"]["time"] if sol["details"]["time"] else "0–5 min"
                                composition_old = sol["details"]["composition_name"]
                                composition_chems = sol["details"]["composition_chems"]

                time_arr = [
                    "0–5 min", "5–10 min", "10–15 min", "15–30 min", "30–60 min",
                    "1–2 h", "2–4 h", "4–8 h", "8–16 h"
                ]

                st.write("**Incubation details**")
                col3, col4, col5 = st.columns([0.7, 1.5, 2])
                with col3:
                    PH = st.text_input("pH", value=PH_old,
                                       disabled=st.session_state.select_type != "composition_listed",
                                       key=f"{experiment_name}_{solution_name}_ph")
                with col4:
                    temp = st.text_input("Temperature (°C)", value=temp_old,
                                         key=f"{experiment_name}_{solution_name}_temp")
                with col5:
                    time = st.selectbox(
                        "Time",
                        time_arr,
                        key=f"{experiment_name}_{solution_name}_time",
                        index=time_arr.index(time_old)
                    )

                composition_arr = ["Solution details not listed: reference paper",
                                   "Solution details not listed: reference manufacturer",
                                   "Solution details listed"]

                composition = st.radio(
                    "**Composition**",
                    options=composition_arr,
                    horizontal=True,
                    key=f"column_selector_{experiment_name}_{solution_name}",
                    index=composition_arr.index(composition_old)
                )
                st.session_state.select_type = f"composition_{composition.strip().split()[-1]}"

                for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
                    if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                        for j, sol in enumerate(exp["solutions"]):
                            if sol["text"] == solution_name or sol["alt_sol_text"] == solution_name:
                                if st.session_state.select_type == "composition_listed":
                                    st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j][
                                        "details"]["composition_selections"] = []
                                else:
                                    st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j][
                                        "details"]["composition_chems"] = []
                                    st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j][
                                        "details"]["ph"] = "0"
                                    PH = "0"
                                st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j]["details"][
                                    "ph"] = PH
                                st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j]["details"][
                                    "temp"] = temp
                                st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j]["details"][
                                    "time"] = time
                                st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j][
                                    "details"]["composition_name"] = composition

                if st.session_state.select_type == "composition_listed":
                    header_selection = st.radio(
                        "Select:",
                        options=["Name", "Quantity", "Unit"],
                        horizontal=True,
                        key="column_selector"
                    )
                    st.session_state.select_type_composition = f"solution_{header_selection}"

                    flat_list_selection = [{
                        **item,
                        "section": self.tabs[i]
                    } for i, sublist in enumerate(self.selections) for item in sublist]
                    last_item = flat_list_selection[-1] if flat_list_selection else {}

                    if st.session_state.select_type_composition.startswith("solution_Name"):
                        st.session_state.details_listed["name"] = last_item
                    elif st.session_state.select_type_composition.startswith("solution_Quantity"):
                        st.session_state.details_listed["quantity"] = last_item
                    elif st.session_state.select_type_composition.startswith("solution_Unit"):
                        st.session_state.details_listed["unit"] = last_item

                    if st.session_state.details_listed["name"] != {}:
                        st.write(f"Name: {st.session_state.details_listed['name']['text']}")
                    if st.session_state.details_listed["quantity"] != {}:
                        st.write(f"Quantity: {st.session_state.details_listed['quantity']['text']}")
                    if st.session_state.details_listed["unit"] != {}:
                        st.write(f"Unit: {st.session_state.details_listed['unit']['text']}")

                    st.button("Add", on_click=lambda: self.addChems(experiment_name, solution_name,
                                                                    st.session_state.details_listed),
                              use_container_width=True)

                    if len(composition_chems) > 0:
                        st.data_editor(
                            pd.DataFrame([{
                                "type": chem["name"]["tag"],
                                "name": chem["name"]["text"],
                                "quantity": chem["quantity"]["text"],
                                "unit": chem["unit"]["text"],
                            } for chem in composition_chems]),
                            use_container_width=True,
                            column_config={
                                "type": st.column_config.TextColumn("Chemical Type"),
                                "name": st.column_config.TextColumn("Name"),
                                "quantity": st.column_config.TextColumn("Quantity"),
                                "unit": st.column_config.TextColumn("Unit"),
                            },
                            disabled=["type", "name", "quantity", "unit"],
                            key="chems_editor_2")
                else:
                    data = [
                        {"selection": item["text"]}
                        for sublist in self.selections if sublist
                        for item in sublist
                    ]

                    if not data:
                        data = [{"selection": ""}]

                    st.data_editor(
                        pd.DataFrame(data),
                        use_container_width=True,
                        column_config={
                            "selection": st.column_config.TextColumn("Selection"),
                        },
                        disabled=["selection"],
                        key="chems_editor_3")

                    for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
                        if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                            for j, sol in enumerate(exp["solutions"]):
                                if sol["text"] == solution_name or sol["alt_sol_text"] == solution_name:
                                    # flat_list = [{
                                    #     **item,
                                    #     "section": self.tabs[i]
                                    # } for i, sublist in enumerate(self.selections) for item in sublist]
                                    st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j][
                                        "details"]["composition_selections"] = self.selections

                for exp in self.experiments:
                    if exp["text"] in experiment_name or exp["alt_exp_text"] == experiment_name:
                        for sol in exp["solutions"]:
                            if sol["text"] == solution_name or sol["alt_sol_text"] == solution_name:
                                st.session_state.active_solution_widget = sol
                return "PI"

            return "PI"

    def addChems(self, exp_name, sol_name, details):
        for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            if exp["text"] == exp_name or exp["alt_exp_text"] == exp_name:
                for j, sol in enumerate(exp["solutions"]):
                    if sol["text"] == sol_name or sol["alt_sol_text"] == sol_name:
                        name = details["name"]
                        quantity = details["quantity"]
                        unit = details["unit"]

                        if not name:
                            st.warning("Name is emppty")
                            return
                        if not quantity:
                            st.warning("Quantity is emppty")
                            return
                        if not unit:
                            st.warning("Unit is emppty")
                            return

                        properties = {}

                        if name["tag"] == quantity["tag"] and name["tag"] == unit["tag"]:
                            properties = {"name": {**name, "alt_name": ""},
                                          "quantity": {**quantity, "alt_quantity": ""},
                                          "unit": {**unit, "alt_unit": ""}}
                        else:
                            st.warning("Name, Quantity and Unit do not have the same type")
                            return
                        st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][j]["details"][
                            "composition_chems"].append(properties)

    def experiment_details_interactors(self, experiment_name, bait_name, type):
        missing_fields = []

        # Check which fields are empty
        for field in ["name"]:
            if st.session_state.current_interactor.get(field, {}) == {}:
                missing_fields.append(field)

        # If any are missing, show warnings
        if missing_fields:
            for field in missing_fields:
                st.warning(f"Select {field}")
            return

        option = "interactors"
        for i, experiment in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            if experiment["text"] == experiment_name or experiment["alt_exp_text"] == experiment_name:
                baits = st.session_state.subpages[self.index - 1]["experiments"][i]["baits"]
                for j, bait in enumerate(baits):
                    if bait["name"] == bait_name or bait["alt_name"] == bait_name:
                        st.session_state.subpages[self.index - 1]["experiments"][i]["baits"][j]["interactors"].append({
                            "type": type,
                            "name": st.session_state.current_interactor['name']['text'],
                            "alt_name": None,
                            "species": st.session_state.current_interactor['species']['text'] if st.session_state.current_interactor['species'] else None,
                            "alt_species": None,
                            "uuid": str(uuid.uuid4())
                        })

        st.session_state.current_interactor = {
            "name": {},
            "species": {}
        }

    def experiment_details_baits(self, experiment_name, type, control):
        missing_fields = []

        # Check which fields are empty
        for field in ["name"]:
            if st.session_state.current_bait.get(field, {}) == {}:
                missing_fields.append(field)

        # If any are missing, show warnings
        if missing_fields:
            for field in missing_fields:
                st.warning(f"Select {field}")
            return

        option = "baits"

        for i, experiment in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            if experiment["text"] == experiment_name or experiment["alt_exp_text"] == experiment_name:
                st.session_state.subpages[self.index - 1]["experiments"][i][option].append({
                    "type": type,
                    "control": control,
                    "name": st.session_state.current_bait['name']['text'],
                    "alt_name": None,
                    "tag": st.session_state.current_bait['tag']['text'] if st.session_state.current_bait['tag'] else None,
                    "alt_tag": None,
                    "species": st.session_state.current_bait['species']['text'] if st.session_state.current_bait['species'] else None,
                    "alt_species": None,
                    "uuid": str(uuid.uuid4()),
                    "interactors": []
                })
        st.session_state.current_bait = {
            "name": {},
            "tag": {},
            "species": {}
        }

    def colored_card(self, title, subtitle, bg_color="#1f77b4", text_color="#ffffff", key=None):
        if key is None:
            key = str(uuid.uuid4())  # Generate unique key if none provided

        container_id = f"card-{key}"

        st.markdown(f"""
            <div id="{container_id}" style="
            background: linear-gradient(135deg, {bg_color}, #333333);
            padding: 1.5rem;
            border-radius: 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                            color: {text_color};
            font-family: 'Segoe UI', sans-serif;
            margin: 1rem 0;
            ">
            <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.3rem;">
                            {title}
            </div>
            <div style="font-size: 1rem; font-weight: 400; opacity: 0.85;">
                            {subtitle}
            </div>
            </div>
        """, unsafe_allow_html=True)

    def main_page(self, tab_names=None):
        if tab_names:
            self.tabs = tab_names

        if not self.coffee_break_display:
            st.title(self.label)
            self.displayTextHighlighter(self.highlighter_labels, tab_names)
        else:
            # Hide sidebar with CSS
            st.markdown("""
                <style>
                [data-testid="stSidebar"] {display: none;}
                .block-container {padding-top: 4rem;}
                </style>
            """, unsafe_allow_html=True)

            if self.index == 2:
                self.display_coffee_break_1()
            elif self.index == 3:
                self.display_coffee_break_2()
            else:
                self.display_coffee_break_3()

    @st.cache_data
    def get_tab_body(_self, tab_name):
        df = _self.paper_data
        tmp = df[df.section_type == tab_name]
        return tmp['text'].str.cat(sep="\n\n") if not tmp.empty else "No content available for this section."

    def update_labels_type(self, labels):
        self.highlighter_labels = labels

    def displayTextHighlighter(self, labels, tab_names):
        label_names = [l[0] for l in labels]
        tabs = st.tabs(tab_names)
        results = []
        absolute_index = st.session_state.active_experiment_widget.get("absolute_index")
        solution_start_end_sum = st.session_state.active_solution_widget.get("start",
                                                                             0) + st.session_state.active_solution_widget.get(
            "end", 0)
        select_type = st.session_state.select_type
        select_type_composition = st.session_state.select_type_composition
        # st.write(solution_start_end_sum)

        for i, (name, tab) in enumerate(zip(tab_names, tabs)):
            tab_annotations = []
            if len(self.selections) > 0:
                # Filter out annotations with unknown tags
                tab_annotations = [
                    ann for ann in self.selections[i]
                    if ann.get("tag") in label_names
                ]
            with tab:
                result = text_highlighter(
                    text=self.get_tab_body(name),
                    labels=labels,
                    text_height=400,
                    annotations=tab_annotations,
                    key=f"text_highlighter_{name}_{''.join(self.label.split(' '))}_{absolute_index}_{select_type}_{solution_start_end_sum}_{select_type_composition}"
                    # Assign a unique key for each tab
                )
                results.append(result)
        self.selections = results

    def display_coffee_break_1(self):
        experiments = []
        for tab in self.experiments.values():
            for experiment in tab:
                for tab2 in experiment["solutions"]:
                    for solution in tab2:
                        exp = {
                            "type": experiment["type"],
                            "text": experiment["text"],
                            "section": experiment["section"],
                            "absolute_index": experiment["absolute_index"],
                            "alt_text": experiment["alt_exp_text"],
                            "solution": {
                                "type": self.check_tag(solution["tag"]),
                                "text": solution["text"],
                                "alt_text": solution["alt_sol_text"]
                            }
                        }
                        experiments.append(exp)

        print(self.experiments)

        # Fetch Coffee Break A text from interchange.json
        coffee_break_a = detail_picker["coffee_break_a"]
        st.title(detail_picker["title"])
        st.markdown(f"#### {coffee_break_a['title']}")
        st.write(coffee_break_a["body"])

        if self.doi_link:
            st.link_button("Go to full-text paper", self.doi_link)
        else:
            st.markdown("""
                <div style="background-color:#ffdddd; color:#a94442; padding:10px 15px; border-left:6px solid #f44336; border-radius:4px; margin-bottom:15px;">
                ⚠️ DOI link not available for this paper.
                </div>
            """, unsafe_allow_html=True)

        # Editable table for experiments and solutions
        exp_df = pd.DataFrame([
            {
                "exp_name": e["text"],
                "alt_exp_name": e["alt_text"],
                "exp_type": e["type"],
                "section": e["section"],
                "absolute_index": e["absolute_index"],
                "sol_name": e["solution"]["text"],
                "alt_sol_name": e["solution"]["alt_text"],
                "sol_type": e["solution"]["type"]
            }
            for e in experiments
        ])

        edited_df = st.data_editor(
            exp_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "exp_name": st.column_config.TextColumn("Experiment name", disabled=True),
                "alt_exp_name": st.column_config.TextColumn("Alternative Experiment Name"),
                "exp_type": st.column_config.SelectboxColumn(
                    "Experiment Type", options=["PI", "non-PI"]
                ),
                "sol_name": st.column_config.TextColumn("Solution name", disabled=True),
                "alt_sol_name": st.column_config.TextColumn("Alternative Solution Name"),
                "sol_type": st.column_config.SelectboxColumn(
                    "Solution Type", options=["PI", "non-PI"]
                ),
            },
            column_order=("exp_name","alt_exp_name","exp_type","sol_name","alt_sol_name","sol_type"),
            key="exp_editor"
        )

        # Validate and correct Solution Type based on Experiment Type
        corrected = False
        for idx, row in edited_df.iterrows():
            if row["exp_type"] == "non-PI" and row["sol_type"] != "non-PI":
                edited_df.at[idx, "sol_type"] = "non-PI"
                corrected = True

        if corrected:
            st.error("Solution Type was set to 'non-PI' for rows where Experiment Type is 'non-PI'.")
        else:
            self.coffee_break_1_saved = edited_df

    def display_coffee_break_2(self):
        # Fetch Coffee Break B text from interchange.json
        coffee_break_b = detail_picker["coffee_break_b"]
        st.title(detail_picker["title"])
        st.markdown(f"#### {coffee_break_b['title']}")
        st.write(coffee_break_b["body"])

        if self.doi_link:
            st.link_button("Go to full-text paper", self.doi_link)
        else:
            st.markdown("""
                <div style="background-color:#ffdddd; color:#a94442; padding:10px 15px; border-left:6px solid #f44336; border-radius:4px; margin-bottom:15px;">
                ⚠️ DOI link not available for this paper.
                </div>
            """, unsafe_allow_html=True)

        experiment_names = [
            exp["alt_exp_text"] if exp["alt_exp_text"] else exp["text"]
            for exp in self.experiments
            if exp["type"] == "PI"
        ]
        experiment_name = None
        bait_name = None
        bait = {}

        col1, col2 = st.columns([1, 1])
        with col1:
            experiment_name = st.selectbox("Experiment", experiment_names, key="experiment_select")
        with col2:
            baits = []
            for exp in self.experiments:
                if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                    baits = exp["baits"]
            baits_names = [
                bait["alt_name"] if bait["alt_name"] else bait["name"]
                for bait in baits
            ]
            bait_name = st.selectbox("Bait 1", baits_names, key="bait_select")

        current_exp = None

        for exp in self.experiments:
            if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                current_exp = exp
                for bait_obj in exp["baits"]:
                    if bait_obj["name"] == bait_name or bait_obj["alt_name"] == bait_name:
                        bait = bait_obj
        st.markdown("### Bait details:")

        bait_df = None
        if bait:
            bait_df = pd.DataFrame([
                {
                    "uuid": bait["uuid"],
                    "bait_type": bait["type"],
                    "bait_control": bait["control"],
                    "bait_name": bait["name"],
                    "bait_alt_name": bait["alt_name"],
                    "bait_tag": bait["tag"],
                    "bait_alt_tag": bait["alt_tag"],
                    "bait_species": bait["species"],
                    "bait_alt_species": bait["alt_species"],
                }
            ])
        else:
            bait_df = pd.DataFrame([])

        baits_editor = st.data_editor(
            bait_df,
            num_rows="dynamic",
            use_container_width=True,
            key="bait_editor",
            column_config={
                "bait_type": st.column_config.TextColumn("Type", disabled=True),
                "bait_control": st.column_config.TextColumn("Control", disabled=True),
                "bait_name": st.column_config.TextColumn("Name", disabled=True),
                "bait_alt_name": st.column_config.TextColumn("Alt. Name"),
                "bait_tag": st.column_config.TextColumn("Tag", disabled=True),
                "bait_alt_tag": st.column_config.TextColumn("Alt. Tag"),
                "bait_species": st.column_config.TextColumn("Species", disabled=True),
                "bait_alt_species": st.column_config.TextColumn("Alt. Species"),
            },
            column_order = ("bait_type","bait_control","bait_name","bait_alt_name","bait_tag","bait_alt_tag","bait_species","bait_alt_species")
        )

        st.markdown("### Interactor(s) details:")

        interactor_df = None

        if bait:
            interactor_df = pd.DataFrame([
                {
                    "uuid": interactor["uuid"],
                    "bait_name": bait["alt_name"] if bait["alt_name"] else bait["name"] ,
                    "interactor_type": interactor["type"],
                    "interactor_name": interactor["name"],
                    "interactor_alt_name": interactor["alt_name"],
                    "interactor_species": interactor["species"],
                    "interactor_alt_species": interactor["alt_species"],
                } for interactor in bait["interactors"]
            ])
        else:
            interactor_df = pd.DataFrame([])

        interactors_editor = st.data_editor(
            interactor_df,
            num_rows="dynamic",
            use_container_width=True,
            key="interactor_editor",
            column_config={
                "bait_name": st.column_config.TextColumn("Bait Name", disabled=True),
                "interactor_type": st.column_config.TextColumn("Type", disabled=True),
                "interactor_name": st.column_config.TextColumn("Name", disabled=True),
                "interactor_alt_name": st.column_config.TextColumn("Alt. Name"),
                "interactor_species": st.column_config.TextColumn("Species", disabled=True),
                "interactor_alt_species": st.column_config.TextColumn("Alt. Species"),
            },
            column_order = ("bait_name","interactor_type","interactor_name","interactor_alt_name","interactor_species","interactor_alt_species")
        )

        self.coffee_break_2_saved = {
            "baits": baits_editor,
            "interactors": interactors_editor,
            "experiment": current_exp
        }

    def display_coffee_break_3(self):
        # Filter experiments to only those with at least one PI solution
        filtered_experiments = []
        for exp in self.experiments:
            solutions = exp.get("solutions", [])
            if solutions and isinstance(solutions[0], list):
                flat_solutions = [item for sublist in solutions for item in sublist]
            else:
                flat_solutions = solutions
            if any(sol.get("type") == "PI" for sol in flat_solutions if isinstance(sol, dict)):
                filtered_experiments.append(exp)

        experiment_names = [
            exp["alt_exp_text"] if exp.get("alt_exp_text") else exp["text"]
            for exp in filtered_experiments
        ]

        experiment_name = None
        solution_names = []
        solution_name = None
        solution = {}
        experiment = {}
        altered_solution = {}

        # Fetch Coffee Break C text from interchange.json
        coffee_break_c = detail_picker["coffee_break_c"]
        st.title(detail_picker["title"])
        st.markdown(f"#### {coffee_break_c['title']}")
        st.write(coffee_break_c["body"])

        if self.doi_link:
            st.link_button("Go to full-text paper", self.doi_link)
        else:
            st.markdown("""
                <div style="background-color:#ffdddd; color:#a94442; padding:10px 15px; border-left:6px solid #f44336; border-radius:4px; margin-bottom:15px;">
                ⚠️ DOI link not available for this paper.
                </div>
            """, unsafe_allow_html=True)

        # Dropdowns
        col1, col2 = st.columns([1, 1])
        with col1:
            experiment_name = st.selectbox("Experiment", experiment_names, key="exp_type_3")

        for exp in self.experiments:
            if exp["text"] in experiment_name or exp["alt_exp_text"] in experiment_name:
                experiment = exp
                solution_names = [
                    sol["alt_sol_text"] if sol["alt_sol_text"] else sol["text"]
                    for sol in exp["solutions"]
                    if sol["type"] == "PI"
                ]
                break

        with col2:
            solution_name = st.selectbox("Solution Type", solution_names, key="sol_type_3")

        for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            if exp["text"] == experiment_name or exp["alt_exp_text"] == experiment_name:
                for j, sol in enumerate(exp["solutions"]):
                    if sol["text"] == solution_name or sol["alt_sol_text"] == solution_name:
                        solution = sol

        time_arr = [
            "0–5 min", "5–10 min", "10–15 min", "15–30 min", "30–60 min",
            "1–2 h", "2–4 h", "4–8 h", "8–16 h"
        ]

        # pH, Temperature, Time
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            new_ph = st.text_input("pH", value=solution["details"]["ph"],
                                   disabled=solution["details"]["composition_name"] != "Solution details listed")
        with col2:
            new_temp = st.text_input("Temperature (°C)", value=solution["details"]["temp"], key="temperature_input")
        with col3:
            new_time = st.selectbox(
                "Time",
                time_arr,
                key=f"{experiment_name}_{solution_name}_time_c_b",
                index=time_arr.index(solution["details"]["time"])
            )

        st.markdown(f"##### {solution['details']['composition_name']}")

        if solution["details"]["composition_name"] == "Solution details listed":
            # Editable table for solution details
            solution_df = pd.DataFrame([
                {
                    "index": i,
                    "tag": chem["name"]["tag"],
                    "name": chem["name"]["text"],
                    "alt_name": chem["name"]["alt_name"],
                    "quantity": chem["quantity"]["text"],
                    "alt_quantity": chem["quantity"]["alt_quantity"],
                    "unit": chem["unit"]["text"],
                    "alt_unit": chem["unit"]["alt_unit"]
                }
                for i, chem in enumerate(solution["details"]["composition_chems"])])
            altered_df = st.data_editor(
                solution_df,
                num_rows="dynamic",
                use_container_width=True,
                key="solution_editor_coffee_break_3",
                column_config={
                    "index": st.column_config.TextColumn("Nr.", disabled=True),
                    "tag": st.column_config.SelectboxColumn(
                        "Chemical type",
                        options=[
                            "Buffer", "Salt", "Detergent", "Enzyme", "Inhibitor",
                            "Reducing agent", "Substrate", "Other"
                        ]
                    ),
                    "name": st.column_config.TextColumn("Name", disabled=True),
                    "alt_name": st.column_config.TextColumn("Alternative Name", ),
                    "quantity": st.column_config.TextColumn("Quantity", disabled=True),
                    "alt_quantity": st.column_config.TextColumn("Alternative Quantity", ),
                    "unit": st.column_config.TextColumn("Unit", disabled=True),
                    "alt_unit": st.column_config.TextColumn("Alternative Unit", ),
                },
                column_order=("tag", "name", "alt_name", "quantity", "alt_quantity", "unit", "alt_unit")
            )

            if len(solution["details"]["composition_chems"]) > 0:
                def get_alt_value(df, i, col):
                    vals = df.loc[df["index"] == i, col].values
                    return vals[0] if len(vals) > 0 else ""

                new_composition_chems = []
                for _, row in altered_df.iterrows():
                    i = row["index"]
                    chem = solution["details"]["composition_chems"][i]

                    new_chem = {
                        **chem,
                        "name": {**chem["name"], "alt_name": get_alt_value(altered_df, i, "alt_name")},
                        "quantity": {**chem["quantity"], "alt_quantity": get_alt_value(altered_df, i, "alt_quantity")},
                        "unit": {**chem["unit"], "alt_unit": get_alt_value(altered_df, i, "alt_unit")},
                    }
                    new_composition_chems.append(new_chem)

                altered_solution = {
                    **solution,
                    "details": {
                        **solution["details"],
                        "ph": new_ph,
                        "temp": new_temp,
                        "time": new_time,
                        "composition_chems": new_composition_chems,
                    },
                }

            else:
                altered_solution = {
                    **solution,
                    "details": {
                        **solution["details"],
                        "ph": new_ph,
                        "temp": new_temp,
                        "time": new_time,
                    }
                }

            #
            # for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            #     if exp["text"] == experiment_name:
            #         for j, sol in enumerate(exp["solutions"]):
            #             if sol["text"] == solution_name:
            #                 st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][
            #                     j] = altered_solution
        else:
            data = [
                {"selection": item["text"]}
                for sublist in solution["details"]["composition_selections"] if sublist
                for item in sublist
            ]

            st.data_editor(
                pd.DataFrame(data),
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "selection": st.column_config.TextColumn("Selection"),
                },
                disabled=["selection"],
                key="chems_editor_10")

            altered_solution = {
                **solution,
                "details": {
                    **solution["details"],
                    "temp": new_temp,
                    "time": new_time,
                }
            }


        self.coffee_break_3_saved = {
            "experiment": experiment,
            "solution": solution,
            "altered_solution": altered_solution
        }

            # st.write(altered_solution)

            # for i, exp in enumerate(st.session_state.subpages[self.index - 1]["experiments"]):
            #     if exp["text"] == experiment_name:
            #         for j, sol in enumerate(exp["solutions"]):
            #             if sol["text"] == solution_name:
            #                 st.session_state.subpages[self.index - 1]["experiments"][i]["solutions"][
            #                     j] = altered_solution

    def display_coffee_break_nav_buttons(self,
                                         index, pmid, cookies,
                                         prev, save, next,reload,
                                         get_user_key, get_token, add_completed_paper, clear_paper_in_progress
                                         ):
        is_last_page = index == len(st.session_state.subpages) - 1

        col_prev, col_save, col_reload, col_save_next = st.columns([1, 1, 1, 2])
        with col_prev:
            if st.button("Prev", use_container_width=True, key=f"cb_prev_{index}"):
                prev()
        with col_save:
            if st.button("Save", use_container_width=True, key=f"cb_save_{index}"):
                save()
        with col_reload:
            if st.button("Refresh", use_container_width=True, key=f"cb_refresh_{index}"):
                reload()
        with col_save_next:
            if is_last_page:
                if st.button("Save & next", use_container_width=True, key=f"cb_save_next_{index}"):
                    st.session_state["completed_paper"] = pmid
                    cookies["completed_paper"] = pmid

                    if "selected_paper" in st.session_state:
                        del st.session_state["selected_paper"]
                    cookies["selected_paper"] = ""

                    if "paper_in_progress" in st.session_state:
                        del st.session_state["paper_in_progress"]
                    cookies["paper_in_progress"] = ""
                    cookies.save()

                    user_key = get_user_key(cookies)
                    token = get_token(cookies)
                    if user_key:
                        # Only clear after add_completed_paper succeeds
                        if add_completed_paper(user_key, pmid):
                            clear_paper_in_progress(user_key, token)

                    if "pages" in st.session_state:
                        del st.session_state["pages"]
                    if "current_page" in st.session_state:
                        del st.session_state["current_page"]

                    save_annotations_to_db(st.session_state, user_key, pmid, token)

                    st.set_option("client.showSidebarNavigation", True)
                    st.switch_page("pages/7_thanks.py")
            else:
                if st.button("Save & next", use_container_width=True, key=f"cb_save_next_{index}"):
                    save()
                    next()

    def display_abandon_paper_button(
            self, index, pmid, cookies,
            prev, save, next,
            get_user_key, get_token, add_completed_paper, clear_paper_in_progress,
            fetch_user_info, set_abandon_limit, abandon_paper
    ):
        user_key = get_user_key(cookies)
        token = get_token(cookies)
        success, user_info = fetch_user_info(user_key, token)
        if not success:
            st.error(user_info)
            return

        papers_abandoned = user_info.get("AbandonedPMIDs", []) or []
        num_abandoned = len(papers_abandoned)
        max_abandonments = 2
        remaining_restarts = max(0, max_abandonments - num_abandoned)
        abandon_limit_reached = user_info.get("AbandonLimit", False)

        if "show_abandon_confirm" not in st.session_state:
            st.session_state["show_abandon_confirm"] = False

        # Use the same column layout as your nav buttons
        col_abandon, _, _ = st.columns([1, 1, 2])
        with col_abandon:
            if st.button("Abandon Paper", type="secondary", use_container_width=True, disabled=abandon_limit_reached,
                         key=f"abandon_{index}"):
                if remaining_restarts == 1:
                    st.session_state["show_abandon_confirm"] = True
                else:
                    if user_key and pmid:
                        abandon_paper(user_key, pmid, token)
                        clear_paper_in_progress(user_key, token)
                    for key in [
                        "paper_in_progress", "selected_paper", "completed_paper",
                        "cards", "current_page", "pages", "active_solution_btn",
                        "paper_data", "tab_names", "doi_link"
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                        if key in cookies:
                            cookies[key] = ""
                    cookies.save()
                    st.success("Paper abandoned. Returning to paper selection.")
                    st.switch_page("pages/2_pick_paper.py")

        if st.session_state.get("show_abandon_confirm", False):
            st.warning("Are you sure you want to abandon this paper? This is your last allowed restart!")
            col_confirm, col_cancel = st.columns([1, 1])
            with col_confirm:
                if st.button("Yes, abandon", key=f"confirm_abandon_{index}"):
                    if user_key and pmid:
                        abandon_paper(user_key, pmid, token)
                        clear_paper_in_progress(user_key, token)
                    for key in [
                        "paper_in_progress", "selected_paper", "completed_paper",
                        "cards", "current_page", "pages", "active_solution_btn",
                        "paper_data", "tab_names", "doi_link"
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                        if key in cookies:
                            cookies[key] = ""
                    cookies.save()
                    set_abandon_limit(user_key, token)
                    st.session_state["show_abandon_confirm"] = False
                    st.success("Paper abandoned. Returning to paper selection.")
                    st.switch_page("pages/2_pick_paper.py")
            with col_cancel:
                if st.button("Cancel", key=f"cancel_abandon_{index}"):
                    st.session_state["show_abandon_confirm"] = False
