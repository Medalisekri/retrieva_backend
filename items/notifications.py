# items/notifications.py
import requests
from django.conf import settings

ONESIGNAL_URL = "https://onesignal.com/api/v1/notifications"

def send_push(onesignal_ids, title, body, data=None):
    ids = [i for i in onesignal_ids if i]   # drop empties
    if not ids:
        return None

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "include_subscription_ids": ids,
        "headings": {"en": title},
        "contents": {"en": body},
    }
    if data:
        payload["data"] = data

    resp = requests.post(
        ONESIGNAL_URL,
        json=payload,
        headers={
            "Authorization": f"Key {settings.ONESIGNAL_REST_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    return resp.json()
def send_match_notifications(new_item, matches):
    for match in matches:
        new_owner_id   = new_item.user.profile.onesignal_id
        match_owner_id = match.user.profile.onesignal_id

        # tell the new item's owner about the existing match
        send_push(
            [new_owner_id],
            "Possible match found!",
            f"An item matching '{new_item.name}' was reported: {match.name}",
            data={"item_id": match.id},
        )
        # tell the existing item's owner about the new item
        send_push(
            [match_owner_id],
            "Possible match found!",
            f"An item matching '{match.name}' was just reported: {new_item.name}",
            data={"item_id": new_item.id},
        )