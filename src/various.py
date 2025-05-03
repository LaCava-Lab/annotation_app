def evaluate_userID_format(userid):
    if not userid.isdigit():
        return "PIN must contain only digits."

    if len(userid) <= 3:
        return "PIN must be longer than 3 digits."

    return None  # Means it's valid

def evaluate_userID(userid):
	'''
	userid is a string of digits 0-9, of variable length
	
	> n: papers (2)
	Test IDs (min, max): 111219, 9991971
	
	> n: papers (9)
	Test IDs (min, max): 111996, 9998964
	'''
	#userid should be all numbers and no letters
	try:
		float(userid)
	except:
		return False

	#userid should encode an integer value (number of papers n) ranging from 2 to 9.
	m = float(userid[:3])
	[a, b, c] = [float(no) for no in userid[:3]]
	s = a+b+c
	e = float(userid[3:])
	try:
		n = (e + s)/m
	except:
		return False
	if (n == int(n)) and (n in list(range(2,10))):
		return True
	else:
		return False

def evaluate_email(email):
	import re

	academic_email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
	
	return re.fullmatch(academic_email_pattern, email)

