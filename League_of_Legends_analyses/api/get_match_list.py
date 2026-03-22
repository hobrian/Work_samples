import argparse
import requests
import time
import json

import pandas as pd
import numpy as np

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def get_ranked_matches(puuid, config, key_index = 0):
    api_keys = config['api_keys']

    current_key = api_keys[key_index]
    url = f"https://{config['routing']}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

    HEADERS = {"X-Riot-Token": current_key}

    params = {
        "startTime": config['start_time'], 
        "endTime": config['end_time'],
        "queue": 420,
        "start": 0,
        "count": config['match_count']
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers["Retry-After"])
        print(f"Key {current_key[:16]}... rate limited. Sleeping {retry_after}s...")
        time.sleep(retry_after)
        response = requests.get(url, headers={"X-Riot-Token": api_keys[key_index]}, params=params)
        if response.status_code == 200:
            return response.json()
    elif response.status_code == 403:
        print(f"Key {current_key[:16]}... is invalid or banned. Skipping.")
    else:
        print(f"Unexpected status {response.status_code} for puuid {puuid}")
    

    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to config JSON file")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    filenam = config['summoner_df_file']
    summonernames_used = []
    summoner_df = pd.read_csv(filenam,sep='\t')
    
    summoner_df = summoner_df.sample(frac=1,replace=False)
    new_game_count = [50, 50, 50, 50, 50]
    row = 0
    game_list = []
    key_index = 0
    
    try:
        while np.sum(new_game_count) > 15:
            list_len = len(game_list)
            matches = get_ranked_matches(summoner_df.iloc[row,0], config, summoner_df.iloc[row,-1])

            if not matches:
                row+=1
                summonernames_used.append(summoner_df.iloc[row,0])
                continue
            
            game_list = list(set(game_list + list(matches)))
            
            new_game_count.pop(0)
            new_game_count.append(len(game_list)-list_len)
            row+=1
            summonernames_used.append(summoner_df.iloc[row,0])
            if row % 100 == 0:
                print(row)
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        pd.DataFrame(summonernames_used).to_csv(config["summoner_used_file"],sep='\t',header=None,index=None)
        pd.DataFrame(game_list).to_csv(config["match_list_file"],sep='\t',header=None,index=None)