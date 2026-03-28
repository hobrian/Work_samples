# League of Legends Champion Analysis

Personal data science project using the **Riot Games API** to analyze 
champion performance and matchup dynamics in League of Legends.

> 🚧 **Work in Progress** — additional analyses are actively being added.

### App List
🔗 [Counterpick Coverage Tool](https://lol-counterpick-coverage.streamlit.app/)

---

## Project Goals

- Pull and process match data via the Riot Games API
- Perform quality control and data cleaning on raw match records
- Analyze champion-vs-champion matchup outcomes in Emerald+ for patch 16.5
- Build predictive models for matchup win rates

## Project Structure
```
League_of_Legends_analyses/
├── api/                        
│   ├── get_summoner_list.py            # pulls summoner IDs and tracks API key for decryption
│   ├── get_match_list.py               # queries matches by summoner ID - initializes output files
│   ├── update_match_list.py            # queries matches by summoner ID - updates output files
│   ├── get_match_history.py            # queries match history by match ID - intializes output files
│   └── update_match_history.py         # queries match history by match ID - updates output files
├── Jupyter notebooks/
│   ├── riot_queried_summoners.ipynb    # statistical analysis of summoner query sample
│   └── match_history_qc.py             # Sankey visualizations of filtering of match histories
├── streamlit_apps/
│   ├── winrate_role/                   # Streamlit app showing win rates & tool to identify champions that cover counterpicks
```

## Data Source

Match data is collected via the **[Riot Games API](https://developer.riotgames.com/)**. Raw data to be published in `riot_data` folder. 

## Setup

A `config.json` file is used to store API credentials and pipeline settings. I used 3 jsons to query NA, EUW, and KR simultaneously.
```json
{
    "api_keys": [
        "your_api_key_here",
        "your_api_key_here"
    ],
    "routing": "americas",
    "region": "na1",
    "summoner_df_file": "data/summoner_df_na.tsv",
    "match_list_file": "data/match_list_na.txt",
    "summoner_used_file": "data/summoner_used_na.tsv",
    "match_history_file": "data/match_history_na.tsv",
    "matches_used_file": "data/matches_used_na.txt",
    "start_time": 1772697600,
    "end_time": 1773644400,
    "queue": 420,
    "match_count": 30
}
```

| Field | Description |
|---|---|
| `api_keys` | List of Riot API keys — multiple keys supported for rate limit management |
| `routing` | Riot routing region  |
| `region` | Platform region |
| `summoner_df_file` | Output path for summoner metadata |
| `match_list_file` | Output path for collected match IDs |
| `summoner_used_file` | Tracks which summoners have been queried |
| `match_history_file` | Output path for full match history data |
| `matches_used_file` | Tracks which matches have been processed |
| `start_time` | Unix timestamp for match collection window start  (limits data collection to a singular patch) |
| `end_time` | Unix timestamp for match collection window end (limits data collection to a singular patch) |
| `queue` | Riot queue ID (`420` = Ranked Solo/Duo) |
| `match_count` | Number of matches to pull per summoner |

## Skills Demonstrated

- REST API data collection
- Data cleaning and quality control
- Exploratory data analysis
- Bayesian statistics
- *(upcoming)* Machine learning
