import requests

bot_token = "PAST Bot Token Here"
url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

response = requests.get(url)
print(response.text)
