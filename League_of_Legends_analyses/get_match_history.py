import argparse
import json
import requests
import time
from collections import defaultdict

import pandas as pd
import numpy as np

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def get_available_key(api_keys, key_available_at):
    """Return the index of the first available key, or sleep until one is free."""
    while True:
        now = time.time()
        for i, key in enumerate(api_keys):
            if now >= key_available_at[i]:
                return i
        min_wait = min(key_available_at[i] - now for i in range(len(api_keys)))
        print(f"All keys rate limited. Waiting {min_wait:.1f}s...")
        time.sleep(min_wait)

def get_match_history(matchId, config, key_available_at):
    api_keys = config['api_keys']

    url = f"https://{config['routing']}.api.riotgames.com/lol/match/v5/matches/{matchId}"

    while True:
        key_index = get_available_key(api_keys, key_available_at)
        headers = {"X-Riot-Token": api_keys[key_index]}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Key {key_index} rate limited for {retry_after}s.")
            key_available_at[key_index] = time.time() + retry_after
        elif response.status_code == 403:
            print(f"Key {key_index} is invalid or banned.")
            key_available_at[key_index] = float('inf')
        else:
            print(f"Unexpected status {response.status_code} for match {matchId}")
            return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to config JSON file")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    matches_used = []
    
    game_list = list(pd.read_csv(config['match_list_file'],sep='\t',header=None).loc[:,0])
    game_info = []
    row=0
    key_available_at = defaultdict(float)

    colnams = ['matchId', 'patch', 'gameDuration'] + \
        ['puuid_summoner'+str(i) for i in range(1,11)] + \
        ['champion_summoner'+str(i) for i in range(1,11)] + \
        ['role_summoner'+str(i) for i in range(1,11)] + \
        ['blue_win','red_win','surrender','earlysurrender']
    
    try:
        while row < 200:
            out = get_match_history(game_list[row], config, key_available_at)
            if out is not None:
                game_info.append([game_list[row]] + \
                    [out['info']['gameVersion']] + \
                    [out['info']['gameDuration']] + \
                    [out['info']['participants'][i]['puuid'] for i in range(0,10)] + \
                    [out['info']['participants'][i]['championName'] for i in range(0,10)] + \
                    [out['info']['participants'][i]['teamPosition'] for i in range(0,10)] + \
                    [out['info']['teams'][0]['win']] + \
                    [out['info']['teams'][1]['win']] + \
                    [out['info']['participants'][0]['gameEndedInSurrender']] + \
                    [out['info']['participants'][0]['gameEndedInEarlySurrender']]
                 )
                            
            matches_used.append(game_list[row])
            row+=1
            if row % 100 == 0:
                print(row)
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        pd.DataFrame(matches_used).to_csv(config['matches_used_file'],sep='\t',header=None,index=None)
        pd.DataFrame(game_info, columns = colnams).to_csv(config['match_history_file'], sep='\t',index=None)