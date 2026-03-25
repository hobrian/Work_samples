import streamlit as st
import os
import pandas as pd
import numpy as np

import plotly.graph_objects as go

def make_figure(sig_df, error_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sig_df.loc[:,'x'],
            y=sig_df.loc[:,'y'], 
            mode='markers',
            # text = sig_df.loc[:,'txt'],
            marker=dict(
                color='blue',
                symbol='diamond'
            ),
            customdata=list(zip(sig_df.loc[:,'opp'], sig_df.loc[:,'champ'], sig_df.loc[:,'opp'])),
            hovertemplate='%{customdata[1]} vs %{customdata[2]}<br>WR: %{x:.3f}<extra></extra>' 
        ))
    fig.add_trace(
        go.Scatter(
            x=error_df.loc[:,'x'],
            y=error_df.loc[:,'y'], 
            mode='markers',
            error_x=dict(
                type='data',
                symmetric=False,
                array=error_df.loc[:,'upper_error'],
                arrayminus=error_df.loc[:,'lower_error'],
                color='white'
            ),
            marker=dict(
                color='red',
                symbol='circle'
            ),
            hoverinfo='skip'
        ))
    fig.add_vline(
        x=0.5,
        line=dict(
            color='green',
            width=1
        )
    )
    fig.update_xaxes(
        title_text='Win Rate'
    )
    fig.update_yaxes(
        tickvals=list(range(len(error_df))),  
        ticktext=error_df.loc[:,'champ'],                    
        tickfont=dict(size=12),
        zeroline=False,
        range=[-0.5, len(error_df) - 0.5]
    )
    fig.update_layout(
        height=2000*len(error_df)/130,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    return fig

st.title("LoL Patch 26.5 Champion Winrate by Role")

texttab1, texttab2 = st.tabs(["Background","Technical Info"])
with texttab1:
    st.text("League of Legends is a 5v5 competitive game where two teams battle to destroy each other's base. Each player controls a champion — a unique character with a distinct set of abilities, strengths, and weaknesses. With over 160 champions available, each brings a different playstyle to the game.")
    st.text("Champions are organized into roles which correspond to positions on the map: top lane, jungle, mid lane, bot lane, and support. Although this is a 5v5 game, the early phase of the game involves facing off directly with their lane opponent in a one on one or two on two setting. A favorable matchup early on can lead to accumulating advantages that help the player contribute to the overall victory.")
    st.text("Before a match begins, teams take turns selecting their champions in a phase called the draft. The draft proceeds in a snake order, so both you and the opposing team sequentially reveal the selected champions. This creates the concept of a counterpick: choosing a champion whose strengths directly exploit the weaknesses of an opponent's champion. Understanding which champions counter which is therefore a core part of competitive League of Legends strategy.")

with texttab2:
    st.subheader("Data Source")
    st.text("Data was collected from Riot Games' public API covering patch 26.5 across the EUW and NA regions, with KR to be incorporated in a future update. Only ranked solo matches from Emerald rank (top ~10% of players) and above are included to ensure the data reflects intentional champion select decisions and consistent gameplay patterns. Matchups with 10 or fewer games are excluded to reduce noise from rarely occurring champion combinations.")
    st.subheader("Statistics")
    st.text("Win rates for each champion matchup are estimated using Bayesian shrinkage, where empirical Bayes is used to fit a Beta prior from each champion's overall matchup distribution via method of moments. Individual matchup win rates are smoothed using this prior and flagged as significant if they fall outside the 99% credible interval of the champion's overall posterior Beta distribution. This approach naturally accounts for sample size and sets a champion-specific significance threshold rather than arbitrary effect size thresholds.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Top","Jungle","Mid","Bot","Support"])
with tab1:
    top_sig = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_sig.tsv'),sep='\t')
    top_error = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_error.tsv'),sep='\t')
    top_fig = make_figure(top_sig, top_error)
    
    st.plotly_chart(top_fig)
with tab2:
    jg_sig = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_sig.tsv'),sep='\t')
    jg_error = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_error.tsv'),sep='\t')
    jg_fig = make_figure(jg_sig, jg_error)
    
    st.plotly_chart(jg_fig)
with tab3:
    mid_sig = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_sig.tsv'),sep='\t')
    mid_error = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_error.tsv'),sep='\t')
    mid_fig = make_figure(mid_sig, mid_error)
    
    st.plotly_chart(mid_fig)
with tab4:
    bot_sig = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_sig.tsv'),sep='\t')
    bot_error = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_error.tsv'),sep='\t')
    bot_fig = make_figure(bot_sig, bot_error)
    
    st.plotly_chart(bot_fig)
with tab5:
    sup_sig = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_sig.tsv'),sep='\t')
    sup_error = pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_error.tsv'),sep='\t')
    sup_fig = make_figure(sup_sig, sup_error)
    
    st.plotly_chart(sup_fig)
