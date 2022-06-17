import configparser
import difflib
import os
import random
import urllib.parse
from typing import List

import requests

CONFIG_FILE_PATH = os.path.join(os.getcwd(), 'config.ini')

if (not os.path.exists(CONFIG_FILE_PATH)):
    raise Exception(f'No configuration file found! ({CONFIG_FILE_PATH})')

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

api_key = config.get('RAPID_API', 'API_KEY')


def determine_answer(question: str, choices: List[str]):
    print(f'\nQuestion: {question}')

    try:
        request_url = 'https://serpapi.com/search.json'
        params = {
            "q": question,
            "hl": "en",
            "gl": "us",
            "api_key": api_key,
        }
        response = requests.get(request_url, params=params, timeout=10)
        response_json = response.json()
        try:
            search_text = str(response_json['answer_box']['answer'])
        except:
            try:
                search_text = str(response_json['answer_box'])
            except:
                search_text = ' '.join(map(
                    lambda r: f'{r["title"]} {str(r["snippet"])}', response_json['organic_results']))
        results = []
        out_list = []
        for choice in choices:
            matcher = difflib.SequenceMatcher(None, search_text, choice)
            score = sum(n for i, j, n in matcher.get_matching_blocks()
                        ) / float(len(choice))
            results.append(score)
            out_list.append([choice, score])
        print(f'Answer: {out_list}')
        answer = choices[results.index(max(results))]
    except:
        print(f'Answer: __TIMEOUT__')
        answer = random.choice(choices)
    return answer
