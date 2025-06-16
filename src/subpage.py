import uuid
import streamlit as st
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect

class Subpage:
    def __init__(self, label, doi_link, paper_data,sidebar_content,selections ,highlighter_labels,coffee_break):
        self.label = label
        self.doi_link = doi_link
        self.sidebar_content = sidebar_content
        self.coffee_break = coffee_break
        self.paper_data = paper_data
        self.highlighter_labels = highlighter_labels
        self.selections = selections
        self.prev_page_context = None
        self.experiments = []
        self.active_experiment = {}

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
                flat_list = [item for sublist in self.experiments.values() for item in sublist]
                flat_solutions = [item for sublist in self.selections for item in sublist]
                a = len(flat_solutions)
                self.active_experiment = TableSelect(header, flat_list, 2, key=f"table_select_{self.label}_{a}")
                self.active_experiment["solutions"] = flat_solutions
                a = len(flat_solutions)
                print(self.active_experiment)
                if self.active_experiment.get("type") == "non-PI":
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

    def main_page(self,tab_names):
        st.title(self.label)
        self.displayTextHighlighter(self.highlighter_labels, tab_names)

    @st.cache_data
    def get_tab_body(_self,tab_name):
        df = _self.paper_data
        tmp = df[df.section_type == tab_name]
        return tmp['text'].str.cat(sep="\n\n") if not tmp.empty else "No content available for this section."

    def update_labels_type(self, labels):
        self.highlighter_labels = labels
    def displayTextHighlighter(self, labels, tab_names):
        tabs = st.tabs(tab_names)
        results = []

        for i, (name, tab) in enumerate(zip(tab_names, tabs)):
            tab_annotations = []
            if len(self.selections) > 0:
                tab_annotations = self.selections[i]

            with tab:
                result = text_highlighter(
                    text=self.get_tab_body(name),
                    labels=labels,
                    text_height=400,
                    annotations=tab_annotations,
                    key=f"text_highlighter_{name}_{self.label}"  # Assign a unique key for each tab
                )
                results.append(result)
        self.selections = results

