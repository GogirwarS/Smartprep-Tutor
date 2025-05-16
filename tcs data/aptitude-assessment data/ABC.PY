import json

# Load original JSON file
with open('reasoning.json', 'r') as infile:
    data = json.load(infile)

# Initialize new JSON structure
converted = {
    "subject": data["subject"],
    "topics": []
}

# Go through each topic and convert
for topic in data["topics"]:
    new_topic = {
        "name": topic["name"],
        "questions": []
    }

    for q in topic["questions"]:
        labels = ['A', 'B', 'C', 'D']
        option_map = {label: opt for label, opt in zip(labels, q["options"])}
        correct_label = next((label for label, opt in option_map.items() if opt == q["answer"]), None)

        new_question = {
            "id": q["id"],
            "question": q["question"],
            "options": option_map,
            "correct_option": correct_label
        }

        new_topic["questions"].append(new_question)

    converted["topics"].append(new_topic)

# Save to new JSON file
with open('reasoning_converted.json', 'w') as outfile:
    json.dump(converted, outfile, indent=2)

print("Conversion complete. Saved as 'questions_converted.json'")
