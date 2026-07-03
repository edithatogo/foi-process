import sys
import os
import json
import time
import uuid

def send_message(recipient, content):
    msg = {
        "msg_id": str(uuid.uuid4())[:8],
        "sender": "leader",
        "recipient": recipient,
        "msg_type": "direct",
        "content": content,
        "timestamp": time.time(),
        "metadata": {}
    }
    inbox_dir = f".swarm/mailboxes/{recipient}/inbox"
    os.makedirs(inbox_dir, exist_ok=True)
    filename = f"{int(time.time() * 1000)}-{msg['msg_id']}.json"
    filepath = os.path.join(inbox_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(msg, f)
    print(f"Sent task to {recipient}: {content[:60]}...")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_agent_task.py <agent_name> <task_description>")
        sys.exit(1)
    send_message(sys.argv[1], " ".join(sys.argv[2:]))
