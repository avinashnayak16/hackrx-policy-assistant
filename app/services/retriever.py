# simple clause selection based on score + simple filtering
from typing import List

def find_relevant_clauses(query: str, candidates: List[dict], score_threshold=0.6):
    # candidates: [{id, score, metadata}]
    chosen = []
    for c in candidates:
        score = c.get('score', 0)
        meta = c.get('metadata', {})
        text = meta.get('text') or meta.get('content') or ''
        chosen.append({'id': c.get('id'), 'text': text, 'score': score, 'meta': meta})
    # sort by score
    chosen = sorted(chosen, key=lambda x: x['score'], reverse=True)
    return chosen
