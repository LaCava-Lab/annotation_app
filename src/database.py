import requests

BACKEND_URL = "http://localhost:3000"

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
        else:
            return False, None
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
        else:
            return None
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
        else:
            return []
    except Exception:
        return []