import json

raw_articles = json.load(open('d:/tcs hacakthon/ticketiq-verification-kit/samples/articles_sample.json', encoding='utf-8'))
normalized = []

for a in raw_articles:
    art_id = a.get('id')
    steps_raw = a.get('steps', [])
    steps_objs = []
    if isinstance(steps_raw, list):
        for idx, s in enumerate(steps_raw, 1):
            if isinstance(s, dict):
                steps_objs.append(s)
            else:
                steps_objs.append({
                    'sourceStepId': f'{art_id}-S{idx}',
                    'order': idx,
                    'text': str(s)
                })
    symptoms = a.get('symptoms', '')
    symptoms_list = [s.strip() for s in symptoms.split(',') if s.strip()] if isinstance(symptoms, str) else symptoms

    keywords = [a.get('category', ''), a.get('subcategory', '')] + symptoms_list[:3]

    subcat = a.get('subcategory', 'issue')
    norm = {
        'id': art_id,
        'articleId': art_id,
        'title': a.get('title'),
        'category': a.get('category'),
        'subcategory': a.get('subcategory'),
        'symptoms': symptoms_list,
        'symptoms_raw': symptoms,
        'possibleCause': a.get('cause', ''),
        'cause': a.get('cause', ''),
        'prerequisites': [a.get('prerequisites', 'Follow standard verification policy.')],
        'steps': steps_objs,
        'validation': f'Verify resolution of {subcat} per runbook.',
        'escalationCondition': a.get('escalation', 'Escalate to Tier-2 if unresolved.'),
        'escalation': a.get('escalation', 'Escalate to Tier-2 if unresolved.'),
        'keywords': keywords,
        'version': '1.0'
    }
    normalized.append(norm)

with open('d:/tcs hacakthon/ticketiq/data/seed/knowledge_articles.json', 'w', encoding='utf-8') as f:
    json.dump(normalized, f, indent=2)

print('Generated normalized knowledge_articles.json with', len(normalized), 'articles')
