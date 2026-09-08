# items/matching.py
from difflib import SequenceMatcher
from .models import Item
from django.utils.timezone import timedelta
from django.utils import timezone
def normalize_name(name):
    return (name or '').lower().strip()


def is_name_match(a, b, threshold=0.6):
    a, b = normalize_name(a), normalize_name(b)
    if not a or not b:
        return False
    # exact or one contains the other ("wallet" in "black wallet")
    if a == b or a in b or b in a:
        return True
    # fuzzy similarity ratio (0.0 → 1.0)
    return SequenceMatcher(None, a, b).ratio() >= threshold


def find_matches(new_item):
    opposite = 'found' if new_item.type == 'lost' else 'lost'

    candidates = Item.objects.filter(
        type=opposite,
        status='active',
        category=new_item.category,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).exclude(user=new_item.user)

    return [c for c in candidates if is_name_match(new_item.name, c.name)]