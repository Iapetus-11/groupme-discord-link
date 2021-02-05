import classyjson as cj
import requests
import atexit
import time

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

    if jj.count > 0:
        for message in jj.messages:
            pass
