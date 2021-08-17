import json

data = {"Eleven": "Millie",
        "Mike": "Finn",
        "Will": "Noah"}

with open('app.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data, ensure_ascii=False))