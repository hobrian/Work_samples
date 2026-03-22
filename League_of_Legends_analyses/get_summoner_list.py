import requests
import time
import json
import argparse

import pandas as pd
import numpy as np

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def get_entries(tier, config, division=None, key_index=0):
    api_keys = config['api_keys']
    out = []
    QUEUE = "RANKED_SOLO_5x5"

    def make_request(url):
        nonlocal key_index
        for attempt in range(len(api_keys)):
            current_key = api_keys[(key_index + attempt) % len(api_keys)]
            headers = {"X-Riot-Token": current_key}
            r = requests.get(url, headers=headers)

            if r.status_code == 200:
                successful_key = (key_index + attempt) % len(api_keys)
                key_index = (key_index + attempt + 1) % len(api_keys)
                return r.json(), successful_key
            elif r.status_code == 429:
                retry_after = int(r.headers.get("Retry-After", 5))
                print(f"Key {current_key[:16]}... rate limited. Trying next key.")
                if attempt == len(api_keys) - 1:
                    print(f"All keys rate limited. Sleeping {retry_after}s...")
                    time.sleep(retry_after)
                    r = requests.get(url, headers={"X-Riot-Token": api_keys[key_index]}, params=None)
                    if r.status_code == 200:
                        successful_key = key_index
                        key_index = (key_index + 1) % len(api_keys)
                        return r.json(), successful_key
            elif r.status_code == 403:
                print(f"Key {current_key[:16]}... is invalid or banned. Skipping.")
            else:
                print(f"Unexpected status {r.status_code}")
                break

        return None, key_index

    if division:
        page_num = 1
        while True:
            url = f"https://{config['region']}.api.riotgames.com/lol/league/v4/entries/{QUEUE}/{tier}/{division}?page={page_num}"
            result, successful_key = make_request(url)

            if not result:
                break

            out += [(player, successful_key) for player in result]
            page_num += 1
            if page_num % 100 == 0:
                print(page_num)
    else:
        url = f"https://{config['region']}.api.riotgames.com/lol/league/v4/{tier.lower()}leagues/by-queue/{QUEUE}"
        result, successful_key = make_request(url)
        if result:
            entries = result.get("entries", [])
            out = [(player, successful_key) for player in entries]

    return out, key_index




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to config JSON file")
    args = parser.parse_args()
    
    config = load_config(args.config)

    key_index = 0
    TIERS = {
        "EMERALD": ["I", "II", "III", "IV"],
        "DIAMOND": ["I", "II", "III", "IV"],
        "MASTER": [None],
        "GRANDMASTER": [None],
        "CHALLENGER": [None]
    }
    
    emerald_plus_summoners = []
    
    for tier, divisions in TIERS.items():
        for division in divisions:
            
            data, key_index = get_entries(tier, config, division, key_index)
            
            for player,successful_key in data:
                emerald_plus_summoners.append({
                    "summonerName": player["puuid"],
                    "tier": tier,
                    "division": player['rank'],
                    "key": successful_key
                })

    pd.DataFrame(emerald_plus_summoners).to_csv(config['summoner_df_file'],sep='\t',index=None)

