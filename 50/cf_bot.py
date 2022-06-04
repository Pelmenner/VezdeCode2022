import json
import requests
import random
from discord.ext import commands

TOKEN = 'TOKEN'

bot = commands.Bot(command_prefix='ps.')

def query_codeforces(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        return None

    result = json.loads(response.content)
    if result["status"] == "FAILED":
        return None
    return result['result']


@bot.command()
async def find_new_task(ctx, *args):
    seen_problems = set()
    for handle in args:
        result = query_codeforces(
            f"https://codeforces.com/api/user.status?handle={handle}")
        if not result:
            continue

        for submission in result:
            seen_problems.add(str(submission['problem'].get(
                'contestId', '')) + submission['problem']['index'])

    problems = query_codeforces(
        'https://codeforces.com/api/problemset.problems')
    if not problems:
        await ctx.send('Error on server(')
        return

    problems = problems['problems']
    while True:
        problem = random.choice(problems)
        if (str(problem['contestId']) + problem['index']) not in seen_problems:
            await ctx.send(f'https://codeforces.com/contest/{problem["contestId"]}/problem/{problem["index"]}')
            break


def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
