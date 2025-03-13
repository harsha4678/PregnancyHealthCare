import requests

url = "https://pregnancy-calculator-api.p.rapidapi.com/pw/conception/post"

payload = { "conception_date": "2022-06-01" }
headers = {
	"x-rapidapi-key": "6e95faeb21msha5bef903ff44bf7p1782a0jsn04c5482d3937",
	"x-rapidapi-host": "pregnancy-calculator-api.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())