
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
    Load papers table as a list of dicts (JSON-like) in the requested format.
    '''
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    papers = []
    for _, row in df.iterrows():
        paper = {
            "PMID": row.get("PMID", ""),
            "DOI_URL": f"https://doi.org/{row['DOI'].strip()}" if row.get("DOI", "").strip() else "",
            "Title": row.get("Title", ""),
            "Authors": [author.strip() for author in row.get("Authors", "").split(";") if author.strip()],
            "Year": int(row.get("Year", "0")) if row.get("Year", "").isdigit() else row.get("Year", ""),
            "Journal": row.get("Journal", ""),
            "Volume": row.get("Volume", ""),
            "Issue": row.get("Issue", ""),
            "Pages": row.get("Pages", ""),
            "Abstract": row.get("Abstract", ""),
            "FirstParagraph": row.get("FirstParagraph", ""),
            "UsersCompleted": [],
            "UsersCurrent": []
        }
        papers.append(paper)
    return papers

def get_paper_metadata_by_pmid(pmid, csv_path="Data_folder/Papers.csv"):
    '''
    Return a dict with metadata for a single paper by PMID in the requested format.
    '''
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    row = df[df["PMID"] == str(pmid)]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "PMID": row.get("PMID", ""),
        "DOI_URL": f"https://doi.org/{row['DOI'].strip()}" if row.get("DOI", "").strip() else "",
        "Title": row.get("Title", ""),
        "Authors": [author.strip() for author in row.get("Authors", "").split(";") if author.strip()],
        "Year": int(row.get("Year", "0")) if row.get("Year", "").isdigit() else row.get("Year", ""),
        "Journal": row.get("Journal", ""),
        "Volume": row.get("Volume", ""),
        "Issue": row.get("Issue", ""),
        "Pages": row.get("Pages", ""),
        "Abstract": row.get("Abstract", ""),
        "FirstParagraph": row.get("FirstParagraph", ""),
        "UsersCompleted": [],
        "UsersCurrent": []
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
            "EntryID": row.get('EntryID', ''),
            "PMID": row.get('filename', ''),
            "Section": row.get('section_type', ''),
            "Type": row.get('subtitle', ''),
            "TextValue": row.get('text', '')
        })
    return sections

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
