# LoL Counterpick Coverage Tool

An interactive web application for analyzing League of Legends champion matchup data and optimizing your champion pool to cover counterpick weaknesses.

🔗 [Live App](https://lol-counterpick-coverage.streamlit.app/)

---

## Overview

Most League of Legends players master a small number of champions rather than trying to learn them all. For those who main a single champion, certain opposing champions will consistently be advantageous due to fundamental kit interactions. Rather than accepting a losing matchup, this tool helps you identify which backup champions to learn so that no matter what the opponent picks in draft, you always have a strong answer ready.

The app has two components:

**Win Rate Graphs** — visualizes every champion's win rate distribution across all matchups by role. Each champion is represented by their empirical win rate and 99% credible interval. Matchup outliers are defined as those whose adjusted win rates fall outside the credible interval. 

**Champion Pool Recommendation** — given your main champion, identifies significant counter-matchups and recommends the optimal set of backup champions to cover your weaknesses. The tool uses a greedy set cover algorithm to find the minimal champion pool that maximally covers your threat set, weighted by matchup frequency.

---

## Data

850k+ games were collected from Riot Games' public API covering patch 26.5 across the EUW, KR, and NA regions. Only ranked solo matches from Emerald rank (top ~10% of players) and above are included to ensure the data reflects intentional champion select decisions and consistent gameplay patterns. Matchups with 20 or fewer games are excluded to reduce noise from rarely occurring champion combinations.

---

## Methodology

**Bayesian Shrinkage**

Win rates for each champion matchup are estimated using Bayesian shrinkage, where empirical Bayes is used to fit a Beta prior from each champion's overall matchup distribution via method of moments. Individual matchup win rates are smoothed using this prior, pulling outlier values toward the champion's mean and naturally accounting for sample size.

**Significance Testing**

A matchup is flagged as significant if its corrected win rate falls outside the 99% credible interval of the champion's overall posterior Beta distribution. This sets a champion-specific significance threshold rather than an arbitrary fixed baseline — a strong champion on a given patch naturally has a higher bar for what counts as a meaningful matchup deviation.

**Dominator Sets**

The champion pool recommendation is framed as a set cover problem. Given a champion's threat set — opponents whose corrected win rates fall outside the lower bound of the credible interval — the greedy algorithm iteratively selects the candidate champion that covers the most remaining uncovered threats. Coverage is determined by whether a candidate's corrected win rate into a threat exceeds a user-selected threshold, and candidates are ranked by weighted coverage where each threat is weighted by the number of games played in that matchup.

---

## Tech Stack

Python, pandas, NumPy, SciPy, Plotly, Streamlit, Riot Games API

