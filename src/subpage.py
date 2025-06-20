import uuid
import pandas as pd
import streamlit as st
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
from process_interchange import detail_picker

class Subpage:
    def __init__(self, index, label, doi_link, paper_data,sidebar_content,selections ,highlighter_labels,coffee_break,coffee_break_display):
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

    def assign_experiments(self, experiments):
        self.experiments = experiments

    def return_data(self):
        return ["a","b"]

    def check_tag(self,tag):
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
                        "text_color": "white"
                    } for inner_sublist in item["solutions"] for inner_item in inner_sublist]
                } for sublist in self.experiments.values() for item in sublist]
                flat_list_solutions = [{
                    **item,
                    "background_color": "#6290C3" if self.check_tag(item["tag"]) == "PI" else "#F25757",
                    "text_color": "white"
                } for sublist in self.selections for item in sublist]

                current_tab = st.session_state.active_experiment_widget.get("section")
                current_index = st.session_state.active_experiment_widget.get("absolute_index")

                if current_tab is not None or current_index is not None:
                    for i,experiment in enumerate(st.session_state.subpages[self.index - 1]["experiments"][current_tab]):
                        if experiment["absolute_index"] == current_index:
                            print(experiment["absolute_index"],self.selections)
                            st.session_state.subpages[self.index - 1]["experiments"][current_tab][i]["solutions"] = self.selections


                st.session_state.active_experiment_widget = TableSelect(header, flat_list_experiments, 2, key=f"table_select_{self.label}_{len(flat_list_experiments)}")

                st.session_state.active_experiment_widget = {
                    **st.session_state.active_experiment_widget,
                    "solutions": flat_list_solutions
                }

                if st.session_state.active_experiment_widget.get("type") == "non-PI":
                    return "non-PI"
                else:
                    return "PI"

            return "PI"

    def colored_card(self,title, subtitle, bg_color="#1f77b4", text_color="#ffffff", key=None):
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

    def main_page(self,tab_names=None):
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
            else: self.display_coffee_break_3()

    @st.cache_data
    def get_tab_body(_self,tab_name):
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
                    key=f"text_highlighter_{name}_{''.join(self.label.split(' '))}_{absolute_index}"
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
                            "alt_text": "",
                            "solution": {
                                "type": self.check_tag(solution["tag"]),
                                "text": solution["text"],
                                "alt_text": ""
                            }
                        }
                        experiments.append(exp)


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
                "Experiment name": e["text"],
                "Alternative Experiment Name": e["alt_text"],
                "Experiment Type": e["type"],
                "Solution name": e["solution"]["text"],
                "Alternative Solution Name": e["solution"]["alt_text"],
                "Solution Type": e["solution"]["type"]
            }
            for e in experiments
        ])

        edited_df = st.data_editor(
            exp_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Experiment name": st.column_config.TextColumn("Experiment name", disabled=True),
                "Alternative Experiment Name": st.column_config.TextColumn("Alternative Experiment Name"),
                "Experiment Type": st.column_config.SelectboxColumn(
                    "Experiment Type", options=["PI", "non-PI"]
                ),
                "Solution name": st.column_config.TextColumn("Solution name", disabled=True),
                "Alternative Solution Name": st.column_config.TextColumn("Alternative Solution Name"),
                "Solution Type": st.column_config.SelectboxColumn(
                    "Solution Type", options=["PI", "non-PI"]
                ),
            },
            key="exp_editor"
        )

        # Validate and correct Solution Type based on Experiment Type
        corrected = False
        for idx, row in edited_df.iterrows():
            if row["Experiment Type"] == "non-PI" and row["Solution Type"] != "non-PI":
                edited_df.at[idx, "Solution Type"] = "non-PI"
                corrected = True

        if corrected:
            st.error("Solution Type was set to 'non-PI' for rows where Experiment Type is 'non-PI'.")
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

        col1, col2 = st.columns([1, 1])
        with col1:
            st.selectbox("Experiment", ["Experiment"], key="experiment_select")
        with col2:
            st.selectbox("Bait 1", ["Bait 1"], key="bait_select")
        st.markdown("### Bait details:")

        bait_df = pd.DataFrame([
            {
                "Bait type 1": "Protein",
                "Bait type 2": "Experimental",
                "Name": "ORF2p",
                "Alt name": "",
                "Tag": "N/A",
                "Alt tag": "",
                "Species": "HEK293T",
                "Alt. species": "H.sapiens",
            }
        ])
        st.data_editor(
            bait_df,
            num_rows="dynamic",
            use_container_width=True,
            key="bait_editor",
            column_config={
                "Bait type 1": st.column_config.TextColumn("Bait type 1", disabled=True),
                "Bait type 2": st.column_config.TextColumn("Bait type 2", disabled=True),
                "Name": st.column_config.TextColumn("Name", disabled=True),
                "Alt name": st.column_config.TextColumn("Alt name"),
                "Tag": st.column_config.TextColumn("Tag"),
                "Alt tag": st.column_config.TextColumn("Alt tag"),
                "Species": st.column_config.TextColumn("Species"),
                "Alt. species": st.column_config.TextColumn("Alt. species"),
            }
        )

        st.markdown("### Interactor(s) details:")

        interactor_df = pd.DataFrame([
            {
                "Bait ref": 1,
                "Interactor type": "protein",
                "Name": "",
                "Alternative name": "N/A",
                "Species": "HEK293T",
                "Alternative species": "H.sapiens",
            }
        ])
        st.data_editor(
            interactor_df,
            num_rows="dynamic",
            use_container_width=True,
            key="interactor_editor",
            column_config={
                "Bait ref": st.column_config.TextColumn("Bait ref", disabled=True),
                "Interactor type": st.column_config.TextColumn("Interactor type", disabled=True),
                "Name": st.column_config.TextColumn("Name", disabled=True),
                "Alternative name": st.column_config.TextColumn("Alternative name"),
                "Species": st.column_config.TextColumn("Species"),
                "Alternative species": st.column_config.TextColumn("Alternative species"),
            }
        )
    def display_coffee_break_3(self):
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
            experiment_type = st.selectbox("Experiment Type", ["PI", "non-PI"], key="exp_type_3")
        with col2:
            if experiment_type == "PI":
                solution_type_options = ["PI", "non-PI"]
            else:
                solution_type_options = ["non-PI"]
            solution_type = st.selectbox("Solution Type", solution_type_options, key="sol_type_3")

        # pH, Temperature, Time
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        with col1:
            st.text_input("pH", value="7.4")
        with col2:
            st.text_input("Temperature (°C)", value="4", key="temperature_input")
        with col3:
            st.selectbox(
                "Time",
                [
                    "0–5 min", "5–10 min", "10–15 min", "15–30 min", "30–60 min",
                    "1–2 h", "2–4 h", "4–8 h", "8–16 h"
                ],
                key="time_select"
            )
        # Radio buttons
        st.radio(
            "Solution details",  # Non-empty label for accessibility
            ["Solution details not listed:", "Solution details listed:"],
            index=1,
            key="solution_details_radio",
            label_visibility="collapsed"  # Hides the label visually
        )

        # Editable table for solution details
        solution_df = pd.DataFrame([
            {
                "Chemical type": "Buffer",
                "Name": "HEPES",
                "Alternative name": "",
                "Quantity": "20",
                "Alternative Quantity": "",
                "Unit": "mM",
                "Alternative unit": ""
            }
        ])
        st.data_editor(
            solution_df,
            num_rows="dynamic",
            use_container_width=True,
            key="solution_editor",
            column_config={
                "Chemical type": st.column_config.SelectboxColumn(
                    "Chemical type",
                    options=[
                        "Buffer", "Salt", "Detergent", "Enzyme", "Inhibitor",
                        "Reducing agent", "Substrate", "Other"
                    ]
                ),
                "Name": st.column_config.TextColumn("Name", disabled=True),
                "Quantity": st.column_config.TextColumn("Quantity", disabled=True),
                "Unit": st.column_config.TextColumn("Unit", disabled=True),
            }
        )

    def display_coffee_break_nav_buttons(self, 
        index, pmid, cookies,
        prev, save, next,
        get_user_key, get_token, add_completed_paper, clear_paper_in_progress
    ):  
        # Detect if this is the last coffee break
        is_last_coffee_break = (
            self.label.lower().startswith("coffee break") and
            index == len(st.session_state.subpages) - 1
        )

        col_prev, col_save, col_save_next = st.columns([1, 1, 2])
        with col_prev:
            if st.button("Prev", use_container_width=True, key=f"cb_prev_{index}"):
                prev()
        with col_save:
            if st.button("Save", use_container_width=True, key=f"cb_save_{index}"):
                save()
        with col_save_next:
            if is_last_coffee_break:
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
            if st.button("Abandon Paper", type="secondary", use_container_width=True, disabled=abandon_limit_reached, key=f"abandon_{index}"):
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