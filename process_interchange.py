import json

with open('interchange.json', 'r') as file:
    data = json.load(file)

# print(data)

resume = data["pages"]["1_resume"]
pick_paper = data["pages"]["2_pick_paper"]
browse_paper = data["pages"]["3_browse_paper"]
question_cascade = data["pages"]["4_question_cascade"]
detail_picker = data["pages"]["5_detail_picker"]
review_submit = data["pages"]["6_review_submit"]
thanks = data["pages"]["7_thanks"]

print(resume)