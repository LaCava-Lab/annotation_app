
import pandas as pd

def connect():
	'''
	function to connect to S3 DB
	WIP
	'''
	data_dir = "/Users/nikiathanasiadou/Documents/Projects/PaperAnnotation/python_code/streamlit_app/AWS_S3"
	return data_dir

def get_userDB():
	'''
	Load users table
	''' 

def get_papersDB(csv_path="Data_folder/Papers.csv"):
    '''
    Load papers table as a list of dicts (JSON-like)
    '''
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    papers = []
    for _, row in df.iterrows():
        paper = {
            "pmid": row["PMID"],
            "doi": row["DOI"],
            "title": row["Title"],
            "authors": row["Authors"],
            "year": row["Year"],
            "journal": row["Journal"],
            "volume": row["Volume"],
            "issue": row["Issue"],
            "pages": row["Pages"],
            "abstract": row["Abstract"]
        }
        papers.append(paper)
    return papers

def get_paper_metadata_by_pmid(pmid, csv_path="Data_folder/Papers.csv"):
    '''
    Return a dict with metadata for a single paper by PMID.
    '''
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    row = df[df["PMID"] == str(pmid)]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "pmid": row.get("PMID", ""),
        "doi": row.get("DOI", ""),
        "title": row.get("Title", ""),
        "authors": row.get("Authors", ""),
        "year": row.get("Year", ""),
        "journal": row.get("Journal", ""),
        "volume": row.get("Volume", ""),
        "issue": row.get("Issue", ""),
        "pages": row.get("Pages", ""),
        "abstract": row.get("Abstract", "")
    }

def to_userDB():
	'''
	Update user's table 
	''' 

def to_papersDB():
	'''
	Update papers table
	''' 

def get_paper_by_pmid(pmid, csv_path="Data_folder/FullText.csv"):
    '''
    Get paper sections by PMID from the full text CSV (csv -> json -> parsing)
    Returns: dict with pmid and sections list
    '''
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    if "EntryID" not in df.columns:
        raise ValueError("FullText CSV must have an 'EntryID' column.")
    paper_df = df[df['EntryID'].astype(str).str.startswith(str(pmid))]
    if paper_df.empty:
        raise ValueError(f"No entries found for PMID {pmid}")
    sections = []
    for _, row in paper_df.iterrows():
        sections.append({
            "section_type": row.get('section_type', ''),
            "subtitle": row.get('subtitle', ''),
            "text": row.get('text', '')
        })
    return {
        "pmid": str(pmid),
        "sections": sections
    }

def get_doi_link_from_papers_csv(pmid, papers_csv_path="Data_folder/Papers.csv"):
    papers_df = pd.read_csv(papers_csv_path, dtype=str)
    row = papers_df[papers_df["PMID"] == str(pmid)]
    if not row.empty:
        doi = row.iloc[0]["DOI"]
        if pd.notna(doi) and doi.strip():
            return f"https://doi.org/{doi.strip()}"
    return None

def to_submit():
	'''Submit the final, checked result'''

def to_save():
	''' Temporary save or update partial result'''
