import classyjson as cj
import requests
import atexit
import time
import os

os.chdir(os.path.join('.', os.path.dirname(__file__)))  # ensure current working directory is correct

try:
    with open("config.json", "r") as f:
        config = cj.load(f)
except FileNotFoundError:
    print("No config.json found, see config.json.example for an example config file.")
    exit(1)

try:
    with open("last_message.txt", "r") as f:
        last_msg_id = f.readline()
except FileNotFoundError:
    last_msg_id = "10"


def exit_handler():
    with open("last_message.txt", "w") as f:
        f.write(last_msg_id)


atexit.register(exit_handler)

while True:
    res = requests.get(
        f"https://api.groupme.com/v3/groups/{config.group_id}/messages",
        params={"since_id": last_msg_id, "token": config.groupme_token, "limit": 10},
    )

    if res.status_code == 200:
        jj = cj.classify(res.json())

        for i, msg in enumerate(reversed(jj.response.messages)):
            content = msg.text

            res = requests.post(
                config.webhook,
                data={
                    "username": msg.name,
                    "avatar_url": msg.avatar_url,
                    "content": (msg.text if msg.text else "​") + "\n".join(a.url for a in msg.attachments if a.type == "image")
                    # "embeds": [{"image": {"url": a.url}} for a in msg.attachments if a.type == "image"],
                },
            )

            if res.status_code == 429:
                res.msgs.insert(i + 1, msg)  # retry after sleeping
                time.sleep(2)
            elif res.status_code not in (200, 204):
                print(f"Uh oh, something went wrong while executing the Discord webhook... {res.status_code} {res.text}")
            else:
                time.sleep(0.5)  # avoid spamming the webhook

        last_msg_id = jj.response.msgs[0].id
    elif res.status_code == 304:
        time.sleep(5)
    else:
        print(f"Oh no! Response wasn't okily dokily... {res.status_code} {res.text}")
        time.sleep(5)

    time.sleep(5)
