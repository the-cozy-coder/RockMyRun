from ..models.VibeProfiles import VibeProfile

def get_all_vibe_profiles(limit=None):

    query = VibeProfile.query

    if limit:
        query = query.limit(limit)

    return query.all()