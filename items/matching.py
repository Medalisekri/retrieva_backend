# items/matching.py
from difflib import SequenceMatcher
from math import radians, cos, sin, asin, sqrt
from .models import Item
from django.utils import timezone
from datetime import timedelta

def normalize_name(name):
    return (name or '').lower().strip()

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth's radius in km
    return c * r

def extract_numbers(text):
    """Extract all numbers from a string."""
    import re
    return set(re.findall(r'\d+', text))

def is_name_match(a, b, threshold=0.75):  # Increased from 0.6
    a, b = normalize_name(a), normalize_name(b)
    if not a or not b:
        return False
    
    # Exact or substring match
    if a == b or a in b or b in a:
        return True
    
    # Check if both contain numbers — if so, numbers must match
    nums_a = extract_numbers(a)
    nums_b = extract_numbers(b)
    if nums_a and nums_b and not nums_a.intersection(nums_b):
        return False  # "iPhone 10" vs "iPhone 16" → no match
    
    # Fuzzy similarity
    return SequenceMatcher(None, a, b).ratio() >= threshold

def find_matches(new_item, max_distance_km=50):
    """Find potential matches within distance and time window."""
    opposite = 'found' if new_item.type == 'lost' else 'lost'
    
    # Get candidates: opposite type, active, same category, last 30 days
    candidates = Item.objects.filter(
        type=opposite,
        status='active',
        category=new_item.category,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).exclude(user=new_item.user)
    
    matches = []
    for candidate in candidates:
        # Check location proximity
        distance = haversine(
            new_item.lat, new_item.long,
            candidate.lat, candidate.long
        )
        if distance > max_distance_km:
            continue  # Too far away
        
        # Check name similarity
        if is_name_match(new_item.name, candidate.name):
            matches.append(candidate)
    
    return matches