import streamlit as st
import os
import pandas as pd
import numpy as np

import plotly.graph_objects as go

def get_icon_url(champ_name):
    if champ_name=='Wukong':
        champ_name='MonkeyKing'
    return f'https://ddragon.leagueoflegends.com/cdn/16.6.1/img/champion/{champ_name}.png'

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

def progress_bar(value, height=8, color='#e32020'):
    pct = value * 100
    ticks = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    tick_marks = ''.join([
        f'<div style="position: absolute; left: {t*100}%; top: 0; height: 100%; width: 1px; background-color: #bbb;"></div>'
        for t in ticks
    ])
    return f"""
    <div style="position: relative; background-color: #d6d6d6; border-radius: 4px; height: {height}px; width: 100%; margin-bottom: 2px; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; background-color: {color}; width: {pct:.1f}%; height: 100%;"></div>
        {tick_marks}
    </div>
    """
st.set_page_config(layout="wide")

# @st.cache_data
def load_full_data():
    return {
        'Top':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_full.tsv'), sep='\t', index_col=0),
        'Jungle':  pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_full.tsv'), sep='\t', index_col=0),
        'Mid':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_full.tsv'), sep='\t', index_col=0),
        'Bot':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_full.tsv'), sep='\t', index_col=0),
        'Support': pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_full.tsv'), sep='\t', index_col=0)
    }

role_full = load_full_data()
st.title("LoL Patch 26.5 Champion Winrate by Role")

texttab1, texttab2 = st.tabs(["Background","Technical Info"])
with texttab1:
    st.text("League of Legends is a 5v5 competitive game where two teams battle to destroy each other's base. Each player controls a champion — a unique character with a distinct set of abilities, strengths, and weaknesses. With over 160 champions available, each brings a different playstyle to the game.")
    st.text("Champions are organized into roles which correspond to positions on the map: top lane, jungle, mid lane, bot lane, and support. Although this is a 5v5 game, the early phase of the game involves facing off directly with their lane opponent in a one on one or two on two setting. A favorable matchup early on can lead to accumulating advantages that help the player contribute to the overall victory.")
    st.text("Before a match begins, teams take turns selecting their champions in a phase called the draft. The draft proceeds in a snake order, so both you and the opposing team sequentially reveal the selected champions. This creates the concept of a counterpick: choosing a champion whose strengths directly exploit the weaknesses of an opponent's champion. Understanding which champions counter which is therefore a core part of competitive League of Legends strategy.")

with texttab2:
    st.subheader("Data Source")
    st.text("Data was collected from Riot Games' public API covering patch 26.5 across the EUW and NA regions, with KR to be incorporated in a future update. Only ranked solo matches from Emerald rank (top ~10% of players) and above are included to ensure the data reflects intentional champion select decisions and consistent gameplay patterns. Matchups with 20 or fewer games are excluded to reduce noise from rarely occurring champion combinations.")
    st.subheader("Statistics")
    st.text("Win rates for each champion matchup are estimated using Bayesian shrinkage, where empirical Bayes is used to fit a Beta prior from each champion's overall matchup distribution via method of moments. Individual matchup win rates are smoothed using this prior and flagged as significant if they fall outside the 99% credible interval of the champion's overall posterior Beta distribution. This approach naturally accounts for sample size and sets a champion-specific significance threshold rather than arbitrary effect size thresholds.")
    st.subheader("About")
    st.markdown("To view more of my LoL-related analyses, check out my github! [GitHub](https://github.com/hobrian/Work_samples/tree/main/League_of_Legends_analyses)")
bigtab1, bigtab2 = st.tabs(['Winrate Graphs', 'Champion Pool Recommendation'])

with bigtab1:  
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

with bigtab2:
    domtab1, domtab2 = st.tabs(['Tool','Instructions'])
    with domtab1:
        # --- role selection ---
        roles = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
        role_urls = {
            'Top': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-top.png',
            'Jungle': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png',
            'Mid': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png',
            'Bot': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-bottom.png',
            'Support': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-utility.png',
        }

        champ_lists = {
            'Top': top_error['champ'].sort_values().tolist(), 
            'Jungle': jg_error['champ'].sort_values().tolist(), 
            'Mid': mid_error['champ'].sort_values().tolist(), 
            'Bot': bot_error['champ'].sort_values().tolist(), 
            'Support': sup_error['champ'].sort_values().tolist()
        }

        role_sig = {
                'Top':     top_sig,
                'Jungle':  jg_sig,
                'Mid':     mid_sig,
                'Bot':     bot_sig,
                'Support': sup_sig
            }
        
        cols = st.columns(5)
        for col, role in zip(cols, roles):
            with col:
                st.markdown(
                    f'<div style="text-align: center;"><img src="{role_urls[role]}" width="40"/></div>',
                    unsafe_allow_html=True
                )
                if st.button(role, use_container_width=True):
                    st.session_state['role'] = role
                    st.session_state['chosen_champions'] = []  # reset on role change
    
        selected_role = st.session_state.get('role', 'Top')
        role_champs = champ_lists[selected_role]
    
        if st.session_state.get('last_role') != selected_role:
            st.session_state['selected_champ'] = role_champs[0]
            st.session_state['last_role'] = selected_role
            st.session_state['chosen_champions'] = [role_champs[0]]
    
        # --- champion selectbox ---
        selected_champ = st.selectbox(
            'Select your champion',
            options=role_champs,
            key='selected_champ'
        )
    
        # reset chosen if main champ changes
        if st.session_state.get('last_champ') != selected_champ:
            st.session_state['chosen_champions'] = [selected_champ]
            st.session_state['last_champ'] = selected_champ
    
        # --- initialize session state ---
        if 'chosen_champions' not in st.session_state:
            st.session_state['chosen_champions'] = [selected_champ]
    
        # --- slider ---
        
        threshold = st.slider(
            'Coverage threshold',
            min_value=0.50,
            max_value=0.55,
            value=0.52,
            step=0.005,
            format="%.3f"
        )
    
        # --- data ---
        sig_df = role_sig[selected_role]
        full_df = role_full[selected_role]
    
        # --- threat set ---
        threats = full_df[
            (full_df['champ'] == selected_champ) &
            (full_df['delta'] == -1)
        ].copy()
        threat_opps = threats['opp'].tolist()
    
        # --- coverage helpers ---
        def get_wr(champ, opp):
            key = f'{champ}_{opp}'
            if key in full_df.index:
                return full_df.loc[key, 'wr_corrected']
            return 0
    
        def get_coverage(chosen, threats):
            coverage = {}
            for opp in threats:
                best_champ = None
                best_wr = 0
                for e in chosen:
                    wr = get_wr(e, opp)
                    if wr > best_wr:
                        best_wr = wr
                        best_champ = e
                coverage[opp] = {'best_champ': best_champ, 'best_wr': best_wr}
            return coverage
    
        def get_candidates(chosen, selected_champ, full_df):
            all_champs = full_df['champ'].unique().tolist()
            excluded = set(chosen + [selected_champ])
            return [c for c in all_champs if c not in excluded]
    
        def score_candidate(e, uncovered, full_df, threshold):
            covered_count = 0
            tiebreak = 0
            for opp in uncovered:
                wr = get_wr(e, opp)
                if wr > threshold:
                    covered_count += 1
                    tiebreak += wr - threshold
            return covered_count, tiebreak
    
        # --- compute coverage state ---
        chosen = st.session_state['chosen_champions']
        coverage = get_coverage(chosen, threat_opps)
        uncovered = [opp for opp in threat_opps 
                     if coverage[opp]['best_wr'] <= threshold]
    
        # --- layout ---
        left, right = st.columns([1, 3])
    
        with left:
            # selected champ icon
            st.markdown(
                f'<div style="text-align: center;"><img src="{get_icon_url(selected_champ)}" width="80"/></div>',
                unsafe_allow_html=True
            )
    
    
             # --- chosen champions ---
            if len(chosen) > 1:
                st.markdown('---')
                st.markdown('**Your coverage set:**')
                cols = st.columns(3)
                for col,champ_nam in zip(cols,chosen[1:]):
                    with col:
                        st.markdown(
                            f'<img src="{get_icon_url(champ_nam)}" width="35"/>',
                            unsafe_allow_html=True
                        )
                if st.button('Undo last'):
                    st.session_state['chosen_champions'].pop()
                    st.rerun()

            st.markdown('---')

            # --- recommendations ---
            if len(chosen) < 3:
                st.markdown('**Recommended backups:**')
                candidates = get_candidates(chosen, selected_champ, full_df)
                scored = []
                for e in candidates:
                    count, tiebreak = score_candidate(e, uncovered, full_df, threshold)
                    scored.append((e, count, tiebreak))
                scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
                top5 = scored[:5]
    
                for e, count, _ in top5:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(
                            f'<div style="text-align: center;"><img src="{get_icon_url(e)}" width="35"/>',
                            unsafe_allow_html=True
                        )
                        if st.button('Add', key=f'add_{e}'):
                            st.session_state['chosen_champions'].append(e)
                            st.rerun()
                    with col2:
                        st.markdown(f'**{e}**')
                        st.markdown(f'{count}/{len(uncovered)} covered')
                        
            else:
                st.info('Coverage set is full.')

            new_champ = st.selectbox(
                'Add a champion',
                options=[nam for nam in role_champs if nam not in [selected_champ]+chosen],
                key='new_champ'
            )
            if st.button('Add', key=f'add2_{new_champ}'):
                st.session_state['chosen_champions'].append(new_champ)
                st.rerun()  
           
    with right:
        if len(threats) == 0:
            st.info(f'{selected_champ} has no significant unfavorable matchups.')
        else:
            cols_per_row = 5
            rows = [threats.iloc[i:i+cols_per_row] 
                    for i in range(0, len(threats), cols_per_row)]

            for row_df in rows:
                cols = st.columns(cols_per_row)
                for col, (_, row) in zip(cols, row_df.iterrows()):
                    opp = row['opp']
                    cov = coverage[opp]
                    is_covered = cov['best_wr'] > threshold
                    display_wr = np.maximum(cov['best_wr'], row['wr_corrected'])

                    with col:
                        # threat icon
                        st.markdown(
                            f'<div style="text-align: center;"><img src="{get_icon_url(opp)}" width="50"/></div>',
                            unsafe_allow_html=True
                        )
                        # bar — green if covered, red if not
                        bar_color = '#2951f2' if is_covered else '#e32020'
                        st.markdown(
                            progress_bar(display_wr, color=bar_color),
                            unsafe_allow_html=True
                        )
                        # covering champion icon
                        if is_covered and cov['best_champ']:
                            st.markdown(
                                f'<div style="text-align: center;"><img src="{get_icon_url(cov["best_champ"])}" width="25"/></div>',
                                unsafe_allow_html=True
                            )

    with domtab2:
        st.subheader('How to Use This Tool')
        st.text("""
            1. Select your role using the position icons at the top of the page
            2. Choose your main champion from the dropdown
            3. Your champion's significant unfavorable matchups will appear as a grid on the right 
            4. Browse the recommended backup champions ranked by how well they cover your threat set
            5. Select a backup champion to add them to your coverage set. The bars will update to reflect how much of your threat set is now covered
            6. Continue adding champions until you're satisfied with your coverage, or enter your own champion to see how it performs
            """
               )
        st.subheader('What are Dominator Sets?')
        st.text("""
            Many League of Legends players choose to master a small number of champions rather than trying to learn them all. For those who "main" a single champion, they can find themselves in a disadvantageous matchup when their opponent picks a counterpick. Rather than playing into a losing matchup, we can find backup champion(s) to cover these weaknesses and exploit the situation. 
            A dominator set is the minimal collection of backup champions that maximally covers your main's unfavorable matchups. The goal isn't to find the single best backup, but the optimal combination of champions that together leave you with no significant blind spots.
            """
               )
        st.subheader('Recommendation Methodology')
        st.text("""
At each step the tool recommends the backup champion that adds the most marginal coverage to your remaining uncovered threats. Coverage is weighted by win rate margin — a champion that beats your threats convincingly contributes more than one that barely edges them out. Once a threat is covered by a champion in your set, additional champions covering the same threat contribute diminishing returns.
While the tool will recommend a set of champs that increases the marginal coverage as much as possible, League of Legends is a game and is meant to be fun! Everyone should play the champs that they enjoy, so you are able to select your own champs to add to the "dominator set" and see how they improve the coverage of your threat set. 
""")
