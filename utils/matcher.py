from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def match_volunteers(volunteers, issues):
    results = []

    for issue in issues:
        best_match = None
        best_score = 0

        for vol in volunteers:
            score = 0

            if similarity(vol['skill'].lower(), issue['issue_type'].lower()) > 0.5:
                score += 50

            if vol['location'].strip().lower() == issue['location'].strip().lower():
                score += 30

            if vol['availability'].lower() == "yes":
                score += 20

            if score > best_score:
                best_score = score
                best_match = vol

        results.append({
            "issue": issue,
            "volunteer": best_match,
            "score": best_score
        })

    return results