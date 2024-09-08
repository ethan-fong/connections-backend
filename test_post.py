import requests
import json

url = "https://connections-backend-production.up.railway.app/api/submit/"

data = {
    "gameId": 1,
    "submittedGuesses": [
        ["+", "**", "-", "//"],
        ["8 % 3", "1 + 1", "4//2", "min(2, 3)"],
        ["range(5,)", "MIN(2, 3)", "Min(2, 2.5)", "7 / / 3"],
        ["and", "assert", "not", "is"]
    ],
    "isGameWon": True,
    "timeToGuess": [13.407, 17.094, 20.291, 22.158]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(data), headers=headers)
print(f"running")
print(response.status_code)
print(response.json())