import streamlit as st
import glob
import pandas as pd
import numpy as np

import plotly.graph_objects as go


st.title("LoL Patch 26.5 Champion Winrate by Role")

st.write(os.getcwd())
st.write(os.listdir('.'))

# st.text("The purpose of this project is to identify which champs are advantageous relative to other champs. Although I compiled match histories from 3 regions (EUW, KR, NA)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Top","Jungle","Mid","Bot","Support"])

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


with tab1:
    top_sig = pd.read_csv('data/top_sig.tsv',sep='\t')
    top_error = pd.read_csv('data/top_error.tsv',sep='\t')
    top_fig = make_figure(top_sig, top_error)
    
    st.plotly_chart(top_fig)
with tab2:
    jg_sig = pd.read_csv('data/jg_sig.tsv',sep='\t')
    jg_error = pd.read_csv('data/jg_error.tsv',sep='\t')
    jg_fig = make_figure(jg_sig, jg_error)
    
    st.plotly_chart(jg_fig)
with tab3:
    mid_sig = pd.read_csv('data/mid_sig.tsv',sep='\t')
    mid_error = pd.read_csv('data/mid_error.tsv',sep='\t')
    mid_fig = make_figure(mid_sig, mid_error)
    
    st.plotly_chart(mid_fig)
with tab4:
    bot_sig = pd.read_csv('data/bot_sig.tsv',sep='\t')
    bot_error = pd.read_csv('data/bot_error.tsv',sep='\t')
    bot_fig = make_figure(bot_sig, bot_error)
    
    st.plotly_chart(bot_fig)
with tab5:
    sup_sig = pd.read_csv('data/sup_sig.tsv',sep='\t')
    sup_error = pd.read_csv('data/sup_error.tsv',sep='\t')
    sup_fig = make_figure(sup_sig, sup_error)
    
    st.plotly_chart(sup_fig)
