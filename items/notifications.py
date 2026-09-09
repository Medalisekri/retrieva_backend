# items/notifications.py
import requests
from django.conf import settings

ONESIGNAL_URL = "https://onesignal.com/api/v1/notifications"

def send_push(external_ids, title, body, data=None):
    # Filter out any empties
    ids = [i for i in external_ids if i]
    print(f"[ONESIGNAL] Sending to external IDs: {ids}")

    if not ids:
        print("[ONESIGNAL] No IDs — skipping")
        return None

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "include_external_ids": ids,   # ← external IDs, not player IDs
        "headings": {"en": title},
        "contents": {"en": body},
    }
    if data:
        payload["data"] = data

    resp = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers={
            "Authorization": f"Key {settings.ONESIGNAL_REST_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    print(f"[ONESIGNAL] Response: {resp.status_code} {resp.text}")
    return resp
def send_match_notifications(new_item, matches):
    for match in matches:
        # Person who owns the EXISTING item (been waiting for a match)
        existing_owner_uid = match.user.username

        # Person who owns the NEW item (just posted it)
        new_owner_uid = new_item.user.username

        # 1️⃣ Tell the EXISTING item's owner: "Someone posted something like yours!"
        send_push(
            external_ids=[existing_owner_uid],
            title="Possible match found! 🔔",
            body=f"A new item '{new_item.name}' looks like your '{match.name}'.",
            data={"item_id": new_item.id},
        )

        # 2️⃣ Tell the NEW item's owner: "Your item matches something!"
        send_push(
            external_ids=[new_owner_uid],
            title="We found a possible match! 🔔",
            body=f"Your '{new_item.name}' may match the existing '{match.name}'.",
            data={"item_id": match.id},
        )