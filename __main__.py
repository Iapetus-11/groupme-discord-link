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
    last_message_id = "-1"


def exit_handler():
    with open("last_message.txt", "w") as f:
        f.write(last_message_id)


atexit.register(exit_handler)

while True:
    res = requests.get(
        f"https://api.groupme.com/v3/groups/{config.group_id}/messages",
        params={"since_id": last_message_id},
    )

    jj = cj.classify(res.json())

    if res.status_code == 200:
        for message in jj.get("messages", []):
            requests.post(
                config.webhook,
                data={
                    "username": message.name,
                    "avatar_url": message.avatar_url,
                    "content": message.text,
                    "embeds": [{"image": {"url": a.url}} for a in message.attachments if a.type == "image"],
                },
            )
    else:
        print(f"Oh no! Response wasn't okily dokily... {jj}")

    time.sleep(5)
