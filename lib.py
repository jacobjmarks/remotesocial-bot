import difflib
import random
import urllib.parse
from typing import List

import requests


def determine_answer(question, choices: List[str]):
    print(f'Question: {question}')

    try:
        encoded_question = urllib.parse.quote_plus(question)
        request_url = f'https://google-search3.p.rapidapi.com/api/v1/search/q={encoded_question}'
        headers = {
            'X-User-Agent': 'desktop',
            'X-Proxy-Location': 'EU',
            'X-RapidAPI-Key': None,
            'X-RapidAPI-Host': 'google-search3.p.rapidapi.com'
        }
        response = requests.get(request_url, headers=headers, timeout=7)
        response_json = response.json()
        search_text = ' '.join(
            map(lambda r: str(r['description']), response_json['results']))
        results = []
        out_list = []
        for choice in choices:
            matcher = difflib.SequenceMatcher(None, search_text, choice)
            score = sum(n for i, j, n in matcher.get_matching_blocks()) / \
                float(len(choice))
            results.append(score)
            out_list.append([choice, score])
        print(f'Answer: {out_list}')
        answer = choices[results.index(max(results))]
    except:
        print(f'Answer: __TIMEOUT__')
        answer = random.choice(choices)
    return answer
