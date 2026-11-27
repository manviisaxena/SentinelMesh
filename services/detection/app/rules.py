from collections import Counter

def score_event(event, recent_failures=1, reputation=0):
    """Deterministic demo scoring. Scores are triage hints, not proof of compromise."""
    score=0; reasons=[]
    if event.get("event_type")=="login_failed":
        score += 15; reasons.append("failed_login")
    if recent_failures >= 5:
        score += 45; reasons.append("possible_brute_force")
    if event.get("event_type")=="access_denied":
        score += 20; reasons.append("repeated_access_denied")
    if reputation >= 70:
        score += min(35, reputation//3); reasons.append("high_ip_reputation_score")
    score=min(100,score)
    severity="critical" if score>=85 else "high" if score>=65 else "medium" if score>=35 else "low"
    return score,severity,reasons
