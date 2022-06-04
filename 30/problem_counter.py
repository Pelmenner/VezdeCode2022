import requests
import json

handles = input().split()

for handle in handles:
    url = f'https://codeforces.com/api/user.status?handle={handle}&from=1'
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(handle, 0)
        continue

    result = json.loads(response.content)
    if result['status'] == 'FAILED':
        print(handle, 0)
        continue

    solved = set()
    for submission in result['result']:
        if submission['verdict'] == 'OK':
            solved.add(str(submission['problem']['contestId']) + submission['problem']['index'])
    
    print(handle, len(solved))
    