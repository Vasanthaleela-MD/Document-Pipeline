import json

with open("observations.json", "r") as f:
    observations = json.load(f)

fg_observations = []
for observation in observations:
    if observation["doc_id"] in ["F", "G"]:
        fg_observations.append({
            "id": observation["doc_id"] + "_phone",
            "entity_name_guess": "Raj Malhotra",
            "type": "phone_number",
            "extracted_value": observation["value"]
        })

groups={}
for observation in fg_observations:
    key=(
        observation['entity_name_guess'],
        observation['type']
    )

    if key not in groups:
        groups[key]= []
    groups[key].append(observation)
print(groups)

for key, group in groups.items():
    if group[0]["extracted_value"] != group[1]["extracted_value"]:

        group[0]["status"] = "contradictory"
        group[1]["status"] = "contradictory"

        group[0]["conflicts_with"] = group[1]["id"]
        group[1]["conflicts_with"] = group[0]["id"]

def lookup(entity, type):
    result=[]
    for observation in fg_observations:

        if observation["entity_name_guess"] == entity and observation["type"] == type:
            result.append(observation)

    return result

print(lookup("Raj Malhotra", "phone_number"))