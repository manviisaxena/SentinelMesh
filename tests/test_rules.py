import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'services'/'detection'))
from app.rules import score_event

def test_failed_login_is_low_without_pattern():
    score,severity,reasons=score_event({'event_type':'login_failed'},1,0)
    assert score==15 and severity=='low' and 'failed_login' in reasons

def test_bruteforce_and_bad_reputation_escalates():
    score,severity,reasons=score_event({'event_type':'login_failed'},5,95)
    assert score>=85 and severity=='critical'
    assert 'possible_brute_force' in reasons

def test_access_denied_is_scored():
    score,severity,reasons=score_event({'event_type':'access_denied'},1,0)
    assert score==20 and severity=='low'
