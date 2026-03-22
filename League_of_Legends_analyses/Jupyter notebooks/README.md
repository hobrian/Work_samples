# Analyses

Jupyter notebooks containing EDA and statistical validation for the League of Legends champion matchup project. Will contain ML methods as further analyses are performed.

---

## Notebooks

### `riot_queried_summoners.ipynb`
**Summoner Sample Validation**

Statistical analysis validating the summoner dataset collected via the Riot Games API. Includes:

- Visualization of summoner rank distribution across Emerald+ tiers
- Binomial test confirming that simple random sampling produces a representative sample of the ranked population
- Assessment of sampling bias and dataset suitability for downstream matchup analysis


### `match_history_qc.ipynb` 
**Match History Filtering Pipeline**

Sankey visualizations documenting the stepwise filtering of raw match history data, with the following exclusion criteria applied:

- **Patch isolation** — matches restricted to a single game patch to control for balance changes
- **Missing/incorrect labels** — games where roles weren't properly identified were removed
- **Aborted games** — remakes and disconnected games excluded

---

*Additional analysis notebooks will be added as the project develops.*
