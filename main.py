import json
import time

import cloudscraper
from rich.console import Console

console = Console()
session = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'desktop': True
    }
)


def fetch_giveaways():
    try:
        req = session.get('https://legacy.rbxflip-apis.com/giveaways')
        res = req.json()
    except Exception:
        return

    return res.get('data').get('giveaways')


class User:
    users = []

    def __init__(self, token):
        self.joined = set()
        self.headers = {'authorization': f'Bearer {token}'}
        self.identifier = f'Account #{User.users.index(self) + 1}'
        User.users.append(self)

    def join_giveaway(self, giveaway):
        giveaway_id = giveaway.get('_id')
        if giveaway_id in self.joined or giveaway['status'] == 'Closed':
            return

        prize = giveaway.get('item').get('assetId')

        console.print(f'[{self.identifier}] [bold green]Attemping to join giveaway {giveaway_id}[/]')
        req = session.put(f'https://legacy.rbxflip-apis.com/giveaways/{giveaway_id}', headers=self.headers)
        res = req.json()

        if res.get('error', None):
            console.print(f'[{self.identifier}] [bold red]Couldn\'t join giveaway {giveaway_id}[/] (Reason: {res["message"]})')

        if req.status_code == 200:
            console.print(f'[{self.identifier}] [bold green]Joined giveaway {giveaway_id} (Prize: {prize})[/]')

        self.joined.add(giveaway_id)


import itertools

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)
    for token in config.get('access_tokens'):
        User(token)

with console.status('Searching for giveaways...', spinner='bouncingBall') as status:
    while 1:
        if giveaways := fetch_giveaways():
            for giveaway, user in itertools.product(giveaways, User.users):
                user.join_giveaway(giveaway)

        time.sleep(20)
