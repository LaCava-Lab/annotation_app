import requests
import json
import uuid

BACKEND_URL = "https://seal-app-c5ety.ondigitalocean.app"

# -- User Info and Authentication Functions --

def login_user(email, pin):
    """
    Attempt to log in a user. Returns (success, data/message).
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"UserEmail": email.strip(), "UserPIN": pin.strip()},
            timeout=10
        )
        if resp.status_code == 200:
            token = resp.cookies.get("token") or resp.json().get("token")
            user_key = resp.json().get("userKey") or resp.json().get("userID") or email.strip()
            if not token or not user_key:
                return False, "Login failed: No token or userKey received."
            return True, {"token": token, "userKey": user_key}
        else:
            try:
                msg = resp.json().get("error") or resp.json().get("message") or "Login failed."
            except Exception:
                msg = "Login failed."
            return False, msg
    except Exception as e:
        return False, f"Could not connect to backend: {e}"

def signup_user(email, pin):
    """
    Attempt to sign up a user. Returns (success, message).
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={"UserEmail": email.strip(), "UserPIN": pin.strip()},
            timeout=10
        )
        if resp.status_code == 201:
            return True, "Account created! Please log in above."
        else:
            try:
                msg = resp.json().get("error") or resp.json().get("message") or "Sign-up failed."
            except Exception:
                msg = "Sign-up failed."
            return False, msg
    except Exception as e:
        return False, f"Could not connect to backend: {e}"
    
def fetch_user_info(user_key, token):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/users/me",
            params={"userKey": user_key},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, "Could not fetch user info from backend."
    except Exception as e:
        return False, f"Could not connect to backend: {e}"

# -- User Progress Functions --

def abandon_paper(user_key, pmid, token):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/add_abandoned",
            json={"userKey": user_key, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        update_session_status(user_key, pmid, "abandoned", token)
        return resp.status_code == 200
    except Exception:
        return False

def set_abandon_limit(user_key, token):
	try:
		resp = requests.post(
			f"{BACKEND_URL}/users/set_abandon_limit",
			json={"userKey": user_key},
			cookies={"token": token},
			timeout=10
		)
		return resp.status_code == 200
	except Exception:
		return False

def update_paper_in_progress(user_key, pmid, token):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/set_current_pmid",
            json={"userKey": user_key, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False
    
def clear_paper_in_progress(user_key, token):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/set_current_pmid",
            json={"userKey": user_key, "pmid": None},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False
    
def add_completed_paper(user_key, pmid):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/add_completed",
            json={"userKey": user_key, "pmid": pmid},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False
    
def save_session_state(user_key, pmid, session_state, token, question_answers=None):
    """
    Save the current session state to the backend SessionState table.
    If question_answers is provided, include those in the request.
    """
    try:
        payload = {
            "userKey": user_key,
            "pmid": pmid,
            "json_state": json.dumps(session_state)
        }
        
        # Add question answers if provided
        if question_answers:
            payload.update(question_answers)
            
        resp = requests.post(
            f"{BACKEND_URL}/sessions/save",
            json=payload,
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False

def fetch_session_state(user_key, pmid, token):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/sessions/by_user_pmid",
            params={"userKey": user_key, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            # print(f"DEBUG: fetch_session_state response: {data}")
            if "json_state" in data:
                # Accept both dict and string
                if isinstance(data["json_state"], dict):
                    state = data["json_state"]
                else:
                    state = json.loads(data["json_state"])
                # Ensure cards is a list, not a string
                if "cards" in state and isinstance(state["cards"], str):
                    state["cards"] = json.loads(state["cards"])
                return state
        return None
    except Exception:
        return None

def update_session_status(user_key, pmid, status, token):
    """
    Update the SessionStatus field for a session.
    Allowed status values: "open", "closed", "abandoned", "negative"
    """
    try:
        resp = requests.patch(
            f"{BACKEND_URL}/sessions/status",
            json={"userKey": user_key, "pmid": pmid, "status": status},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False
    
# -- "Papers" Functions --

def fetch_all_papers(token):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return True, resp.json()
        elif resp.status_code in (401, 403):
            return False, "Authentication error. Please log in again."
        else:
            return False, f"Failed to fetch papers: {resp.text}"
    except Exception as e:
        return False, f"Could not connect to backend: {e}"

def fetch_paper_info(pmid, token):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers/{pmid}",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return True, resp.json()
        elif resp.status_code in (401, 403):
            return False, "Authentication error. Please log in again."
        else:
            return False, f"Failed to fetch papers: {resp.text}"
    except Exception as e:
        return False, None
    
def fetch_doi_by_pmid(pmid, token):
    """
    Fetch the DOI for a given PMID from the papers table.
    Returns the DOI string if found, otherwise None.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers/{pmid}",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            paper = resp.json()
            doi = paper.get("DOI_URL")
            return doi
        elif resp.status_code in (401, 403):
            return False, "Authentication error. Please log in again."
        else:
            return False, f"Failed to fetch papers: {resp.text}"
    except Exception:
        return None

# -- "Full Text" Functions --

def fetch_fulltext_by_pmid(pmid, token):
    """
    Fetch the fulltext for a given PMID. Returns a list (possibly empty) or None on error.
    """
    try:
        resp = requests.get(
            f"{BACKEND_URL}/fulltext",
            params={"filename": str(pmid)},
            cookies={"token": token},
            timeout=15
        )
        if resp.status_code == 200:
            results = resp.json()
            if results and isinstance(results, list):
                return results
            else:
                return []
        elif resp.status_code in (401, 403):
            return False, "Authentication error. Please log in again."
        else:
            return False, f"Failed to fetch fulltext: {resp.text}"
    except Exception:
        return []

# -- Annotation saving functions --

def save_annotations_to_db(session_state, user_key, pmid, token):
    """
    Save all annotated information from session_state to the backend tables.
    """

    session_id = f"{user_key}_{pmid}"

    # 1. Gather all experiments and solutions
    experiments = []
    solutions = []
    experiment_id_map = {}  # Map experiment text to ExperimentID for reference

    for section, exp_list in session_state["subpages"][1].get("experiments", {}).items():
        for exp in exp_list:
            experiment_id = str(uuid.uuid4())
            experiment_id_map[exp["text"]] = experiment_id
            experiments.append({
                "ExperimentID": experiment_id,
                "SessionID": session_id,
                "name": exp["text"],
                "name_section": exp["section"],
                "name_start": exp["start"],
                "name_end": exp["end"],
                "name_alt": exp.get("name_alt", ""),
                "type": exp["type"]
            })
            # Solutions for this experiment
            for sol_list in exp.get("solutions", []):
                for sol in sol_list:
                    solution_id = str(uuid.uuid4())
                    solutions.append({
                        "SolutionID": solution_id,
                        "ExperimentID": experiment_id,
                        "name": sol["text"],
                        "name_section": exp["section"],
                        "name_start": sol["start"],
                        "name_end": sol["end"],
                        "name_alt": sol.get("name_alt", ""),
                        "type": sol.get("type", exp["type"]),
                    })

    # 2. Gather baits and interactors from Experiment Details
    baits = []
    interactors = []
    for exp in session_state["subpages"][2].get("experiments", []):
        experiment_id = experiment_id_map.get(exp["text"])
        if not experiment_id:
            continue
        for bait in exp.get("baits", []):
            bait_id = str(uuid.uuid4())
            baits.append({
                "BaitID": bait_id,
                "ExperimentID": experiment_id,
                "name": bait.get("name", ""),
                "name_section": exp.get("section", ""),
                "name_start": bait.get("start", None),
                "name_end": bait.get("end", None),
                "name_alt": bait.get("name_alt", ""),
                "species_name": bait.get("species", ""),
                "species_name_section": "",
                "species_name_start": None,
                "species_name_end": None,
                "species_name_alt": "",
                "isControl": bait.get("control", ""),
                "bait_type": bait.get("type", ""),
            })
            for interactor in bait.get("interactors", []):
                interactor_id = str(uuid.uuid4())
                interactors.append({
                    "InteractorID": interactor_id,
                    "BaitID": bait_id,
                    "ExperimentID": experiment_id,
                    "name": interactor.get("name", ""),
                    "name_section": exp.get("section", ""),
                    "name_start": interactor.get("start", None),
                    "name_end": interactor.get("end", None),
                    "name_alt": interactor.get("name_alt", ""),
                    "species_name": interactor.get("species", ""),
                    "species_name_section": "",
                    "species_name_start": None,
                    "species_name_end": None,
                    "species_name_alt": "",
                    "type": interactor.get("type", ""),
                })

    # 3. POST all experiments at once
    if experiments:
        requests.post(
            f"{BACKEND_URL}/experiments",
            json=experiments,
            cookies={"token": token}
        )

    # 4. POST all solutions at once
    if solutions:
        requests.post(
            f"{BACKEND_URL}/solutions",
            json=solutions,
            cookies={"token": token}
        )

    # 5. POST all baits at once
    if baits:
        requests.post(
            f"{BACKEND_URL}/baits",
            json=baits,
            cookies={"token": token}
        )

    # 6. POST all interactors at once
    if interactors:
        requests.post(
            f"{BACKEND_URL}/interactors",
            json=interactors,
            cookies={"token": token}
        )
        
    # Set session status to "closed"
    update_session_status(user_key, pmid, "closed", token)

    return True