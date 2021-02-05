import classyjson as cj
import requests
import atexit
import time
import os

os.chdir(os.path.dirname(__file__))  # ensure current working directory is correct

try:
    with open("config.json", "r") as f:
        config = cj.load(f)
except FileNotFoundError:
    print("No config.json found, see config.json.example for an example config file.")
    exit(1)

try:
    with open("last_message.txt", "r") as f:
        last_message_id = f.readline()
except FileNotFoundError:
    last_message_id = "10"


def exit_handler():
    with open("last_message.txt", "w") as f:
        f.write(last_message_id)


atexit.register(exit_handler)

while True:
    res = requests.get(
        f"https://api.groupme.com/v3/groups/{config.group_id}/messages",
        params={"since_id": last_message_id, "token": config.groupme_token, "limit": 10},
    )

    if res.status_code == 200:
        jj = cj.classify(res.json())

        for i, message in enumerate(reversed(jj.response.messages)):
            res = requests.post(
                config.webhook,
                data={
                    "username": message.name,
                    "avatar_url": message.avatar_url,
                    "content": message.text + "\n".join(a.url for a in message.attachments if a.type == "image")
                    # "embeds": [{"image": {"url": a.url}} for a in message.attachments if a.type == "image"],
                },
            )

            if res.status_code == 429:
                res.messages.insert(i+1, message)  # retry after sleeping
                time.sleep(2)
            elif res.status_code not in (200, 204):
                print(f"Uh oh, something went wrong while executing the Discord webhook... {res.status_code} {res.text}")
            else:
                time.sleep(.5)  # avoid spamming the webhook

        last_message_id = jj.response.messages[0].id
    elif res.status_code == 204:
        pass
    else:
        print(f"Oh no! Response wasn't okily dokily... {res.status_code}")

    time.sleep(5)
