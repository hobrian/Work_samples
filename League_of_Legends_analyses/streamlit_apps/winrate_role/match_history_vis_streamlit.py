import streamlit as st
import os
import pandas as pd
import numpy as np
import requests

import plotly.graph_objects as go

def get_icon_url(champ_name):
    if champ_name=='Wukong':
        champ_name='MonkeyKing'
    return f'https://ddragon.leagueoflegends.com/cdn/16.6.1/img/champion/{champ_name}.png'
def filter_by_class(error_df, sig_df, selected_classes):
    """Filter error_df and sig_df to only include champions in selected classes."""
    def champ_in_classes(champ):
        tags = champ_classes.get(champ, [])
        return any(t in selected_classes for t in tags)
    
    filtered_error = error_df[error_df['champ'].apply(champ_in_classes)].reset_index(drop=True)
    filtered_error['y'] = range(len(filtered_error))  # reindex y positions
    
    # remap sig_df y positions to match filtered error_df
    y_map = {champ: i for i, champ in enumerate(filtered_error['champ'])}
    filtered_sig = sig_df[sig_df['champ'].apply(champ_in_classes)].copy()
    filtered_sig['y'] = filtered_sig['champ'].map(y_map)
    
    return filtered_error, filtered_sig

def class_filter_ui(tab_key):
    """Render horizontal class filter checkboxes, returns list of selected classes."""
    st.markdown('**Filter by class:**')
    cols = st.columns(len(all_classes))
    selected = []
    for col, cls in zip(cols, all_classes):
        with col:
            st.markdown(
                f'<div style="text-align: center; margin-bottom: -15px;"><img src="{class_icon_paths[cls]}" width="30"/></div>',
                unsafe_allow_html=True
            )
            checked = st.checkbox(cls, value=True, key=f'{tab_key}_{cls}', label_visibility='collapsed')
            st.markdown(
                f'<div style="text-align: center; font-size: 16px; margin-top: -10px;">{cls}</div>',
                unsafe_allow_html=True
            )
            if checked:
                selected.append(cls)
    return selected if selected else all_classes

def pagination_ui(df, page_key):
    total_rows = len(df)
    page_size = st.session_state['page_len'] if st.session_state['page_len'] is not None else total_rows
    total_pages = int(max(1, np.ceil(total_rows / page_size)))

    col0, col1, col2, col3, col4 = st.columns([4, 1, 2, 1, 4])
    with col1:
        if st.button("⬅️", key=f'prev_{page_key}', disabled=(st.session_state[page_key] == 1), use_container_width=True):
            st.session_state[page_key] -= 1
            st.rerun()
    with col2:
        st.markdown(f"<div style='text-align: center; line-height: 38px;'><b>Page {st.session_state[page_key]} of {total_pages}</b></div>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️", key=f'next_{page_key}', disabled=(st.session_state[page_key] == total_pages), use_container_width=True):
            st.session_state[page_key] += 1
            st.rerun()
            
    start = (st.session_state[page_key] - 1) * page_size
    end = start + page_size
    st.caption(f"Showing {start + 1}–{min(end, total_rows)} of {total_rows} champions")

    return df.iloc[start:end]
    
def make_figure(sig_df, error_df,sort='Win Rate'):
    fig = go.Figure()
    if sort=='Win Rate':
        y1 = sig_df.loc[:,'y']
        y2 = error_df.loc[:,'y']
        yax_label = error_df.loc[:,'champ']
    elif sort == 'Alphabetical':
        y_dict = {y:x for x,y in enumerate(error_df.sort_values('champ',ascending=False).champ)}
        y1 = [y_dict[i] for i in sig_df.champ]
        y2 = [y_dict[i] for i in error_df.champ]
        yax_label = error_df.sort_values('champ',ascending=False).champ
    fig.add_trace(
        go.Scatter(
            x=sig_df.loc[:,'x'],
            y=y1, 
            mode='markers',
            marker=dict(
                color='blue',
                symbol='diamond'
            ),
            customdata=list(zip(sig_df.loc[:,'opp'], sig_df.loc[:,'champ'], sig_df.loc[:,'opp'], sig_df.loc[:,'total'])),
            hovertemplate='%{customdata[1]} vs %{customdata[2]}<br>WR: %{x:.3f}<br>Games: %{customdata[3]}<extra></extra>' 
        ))
    fig.add_trace(
        go.Scatter(
            x=error_df.loc[:,'x'],
            y=y2, 
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
            width=1.5
        )
    )
    fig.update_xaxes(
        title_text='Win Rate',
        showgrid=True,
        gridwidth=1,
        gridcolor='#454545',
        dtick=0.05
    )
    fig.update_yaxes(
        tickvals=list(range(len(error_df))),  
        ticktext=yax_label,                    
        tickfont=dict(size=12),
        zeroline=False,
        range=[-0.5, len(error_df) - 0.5]
    )
    fig.update_layout(
        height=2000*len(error_df)/130+100,
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    return fig

def progress_bar(value, height=8, color='#e32020', show_tooltip=True):
    pct = value * 100
    ticks = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    tick_marks = ''.join([
        f'<div style="position: absolute; left: {t*100}%; top: 0; height: 100%; width: 1px; background-color: #bbb;"></div>'
        for t in ticks
    ])
    title = f'title="Win Rate: {value:.3f}"' if show_tooltip else ''
    return f"""
    <div {title} style="position: relative; background-color: #d6d6d6; border-radius: 4px; height: {height}px; width: 100%; margin-bottom: 2px; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; background-color: {color}; width: {pct:.1f}%; height: 100%;"></div>
        {tick_marks}
    </div>
    """

@st.cache_data
def load_full_data():
    return {
        'Top':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_full.tsv'), sep='\t'),
        'Jungle':  pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_full.tsv'), sep='\t'),
        'Mid':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_full.tsv'), sep='\t'),
        'Bot':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_full.tsv'), sep='\t'),
        'Support': pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_full.tsv'), sep='\t')
    }

@st.cache_data
def load_sig_data():
    return {
        'Top':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_sig.tsv'),sep='\t'),
        'Jungle':  pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_sig.tsv'),sep='\t'),
        'Mid':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_sig.tsv'),sep='\t'),
        'Bot':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_sig.tsv'),sep='\t'),
        'Support': pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_sig.tsv'),sep='\t')
    }

@st.cache_data
def load_error_data():
    return {
        'Top':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','top_error.tsv'),sep='\t'),
        'Jungle':  pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','jg_error.tsv'),sep='\t'),
        'Mid':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','mid_error.tsv'),sep='\t'),
        'Bot':     pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','bot_error.tsv'),sep='\t'),
        'Support': pd.read_csv(os.path.join(os.getcwd(), 'League_of_Legends_analyses', 'streamlit_apps','winrate_role','data','sup_error.tsv'),sep='\t')
    }

@st.cache_data  
def get_champ_info():
    return requests.get(
        f'https://ddragon.leagueoflegends.com/cdn/16.6.1/data/en_US/champion.json'
    ).json()['data']

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

role_full = load_full_data()
role_sig = load_sig_data()
role_error = load_error_data()

champ_data = get_champ_info()
champ_classes = {}
for key, val in champ_data.items():
    display_name = val['name']
    champ_classes[display_name] = val['tags']
    champ_classes[key] = val['tags']

all_classes = ['Fighter', 'Tank', 'Mage', 'Assassin', 'Marksman', 'Support']
github_raw = 'https://raw.githubusercontent.com/hobrian/Work_samples/main/League_of_Legends_analyses/streamlit_apps/winrate_role/assets'
class_icon_paths = {
    'Fighter':    f'{github_raw}/Fighter_icon.png',
    'Tank':       f'{github_raw}/Tank_icon.png',
    'Mage':       f'{github_raw}/Mage_icon.png',
    'Assassin':   f'{github_raw}/Slayer_icon.png',
    'Marksman':   f'{github_raw}/Marksman_icon.png',
    'Support':    f'{github_raw}/Controller_icon.png',
}

st.title("LoL Patch 26.5 Champion Win Rate by Role")

texttab0, texttab1, texttab2 = st.tabs(["Description","Background","Technical Info"])
with texttab0:
    st.subheader("Win Rate Graphs")
    st.text("""
    Have you ever been in champ select and wondered what champ would be a good counterpick? Looking at matchup data alone is not sufficient. Matchup data does not take into account a champion's overall win rate (is this an advantageous matchup or is my champ just strong in general?), and if there is a small sample size, it is hard to determine what is real and what is noise. These graphs used Bayesian statistics to create intervals where there is a 99% chance that the true win rate of the champ lies within that range. The parameters used to create these intervals are also used to adjust win rates of champion matchups, pulling outlier values towards the mean. I define advantageous and disadvantageous matchups as those whose adjusted win rates fall outside of the 99% credible interval since these deviate from the expected win rate. 
    This tab shows every champion's win rate distribution across all of their matchups in a single view. Each champion is represented by a red dot showing their observed average win rate and a bar showing the 99% interval. The blue diamonds overlaid on each bar represent statistically significant matchups. Advantageous matchups appear on the right, and disadvantageous ones appear on the left. Hover over the diamond to reveal the matchup and see the adjusted win rate and number of games played.
""")
    st.subheader("Champion Pool Recommendation")
    st.text("""
Most players have a main they're most comfortable on, but it always feels bad when your opponent locks in a counterpick before you pick your champ. Do you decide to go into a losing matchup or do you swap champs? Which champ should you swap to? Most importantly, which champ can cover all the matchups that you struggle with on your main? This tool helps you identify which champions you can add to your pool so you always have a winning matchup.
Select your main and the tool identifies which opponents pose a real threat based on win rate data. It then recommends backup champions one at a time, prioritizing whoever covers the most of your remaining bad matchups. You can follow the recommendations or plug in your own favorites to see how well they protect you against your counters.
""")
with texttab1:
    st.text("League of Legends is a 5v5 competitive game where two teams battle to destroy each other's base. Each player controls a champion — a unique character with a distinct set of abilities, strengths, and weaknesses. With over 160 champions available, each brings a different playstyle to the game.")
    st.text("Champions are organized into roles which correspond to positions on the map: top lane, jungle, mid lane, bot lane, and support. Although this is a 5v5 game, the early phase of the game involves facing off directly with their lane opponent in a one on one or two on two setting. A favorable matchup early on can lead to accumulating advantages that help the player contribute to the overall victory.")
    st.text("Before a match begins, teams take turns selecting their champions in a phase called the draft. The draft proceeds in a snake order, so both you and the opposing team sequentially reveal the selected champions. This creates the concept of a counterpick: choosing a champion whose strengths directly exploit the weaknesses of an opponent's champion. Understanding which champions counter which is therefore a core part of competitive League of Legends strategy.")

with texttab2:
    st.subheader("Data Source")
    st.text("850k+ games were collected from Riot Games' public API covering patch 26.5 across the EUW, KR, and NA regions. Only ranked solo matches from Emerald rank (top ~10% of players) and above are included to ensure the data reflects intentional champion select decisions and consistent gameplay patterns. Matchups with 20 or fewer games are excluded to reduce noise from rarely occurring champion combinations.")
    st.subheader("Statistics")
    st.text("Win rates for each champion matchup are estimated using Bayesian shrinkage, where empirical Bayes is used to fit a Beta prior from each champion's overall matchup distribution via method of moments. Individual matchup win rates are smoothed using this prior and flagged as significant if they fall outside the 99% credible interval of the champion's overall posterior Beta distribution. This approach naturally accounts for sample size and sets a champion-specific significance threshold rather than arbitrary effect size thresholds.")
    st.subheader("About")
    st.markdown("To view more of my LoL-related analyses, check out my github! [GitHub](https://github.com/hobrian/Work_samples/tree/main/League_of_Legends_analyses)")

bigtab1, bigtab2 = st.tabs(['Win Rate Graphs', 'Champion Pool Recommendation'])

with bigtab1:
    graph_col1, _, graph_col2,_ = st.columns(4)
    with graph_col1:
        sort_method = st.radio(
            'Sort by',
            options=['Win Rate', 'Alphabetical'],
            horizontal=True
        )
    with graph_col2:
        res_per_page = st.selectbox(
            'Results per page:',
            options=['25','50','All'],
            key='res_num',
        )
        st.session_state['page_len'] = None if res_per_page == 'All' else int(res_per_page)
        
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Top","Jungle","Mid","Bot","Support"])
    if "page_top" not in st.session_state:
        st.session_state['page_top'] = 1

    if st.session_state.get('last_res') != res_per_page:
        for key in ['page_top', 'page_jg', 'page_mid', 'page_bot', 'page_sup']:
            st.session_state[key] = 1
        st.session_state['last_res'] = res_per_page
        
    with tab1:
        selected_classes = class_filter_ui('top')
        filtered_error, filtered_sig = filter_by_class(role_error['Top'], role_sig['Top'], selected_classes)
        if len(filtered_error) == 0:
            st.info('No champions match the selected classes.')
        else:
            page_key = 'page_top'
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
    
            paged_error = pagination_ui(filtered_error, page_key)
    
            paged_error = paged_error.copy()
            paged_error['y'] = range(len(paged_error))
    
            y_map = {champ: i for i, champ in enumerate(paged_error['champ'])}
            paged_sig = filtered_sig[filtered_sig['champ'].isin(paged_error['champ'])].copy()
            paged_sig['y'] = paged_sig['champ'].map(y_map)
    
            top_fig = make_figure(paged_sig, paged_error, sort=sort_method)
            st.plotly_chart(top_fig)
    with tab2:
        selected_classes = class_filter_ui('jg')
        filtered_error, filtered_sig = filter_by_class(role_error['Jungle'], role_sig['Jungle'], selected_classes)
        
        if len(filtered_error) == 0:
            st.info('No champions match the selected classes.')
        else:
            page_key = 'page_jg'
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
    
            paged_error = pagination_ui(filtered_error, page_key)
    
            paged_error = paged_error.copy()
            paged_error['y'] = range(len(paged_error))
    
            y_map = {champ: i for i, champ in enumerate(paged_error['champ'])}
            paged_sig = filtered_sig[filtered_sig['champ'].isin(paged_error['champ'])].copy()
            paged_sig['y'] = paged_sig['champ'].map(y_map)
    
            jg_fig = make_figure(paged_sig, paged_error, sort=sort_method)
            st.plotly_chart(jg_fig)
    with tab3:
        selected_classes = class_filter_ui('mid')
        filtered_error, filtered_sig = filter_by_class(role_error['Mid'], role_sig['Mid'], selected_classes)
        
        if len(filtered_error) == 0:
            st.info('No champions match the selected classes.')
        else:
            page_key = 'page_mid'
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
    
            paged_error = pagination_ui(filtered_error, page_key)
    
            paged_error = paged_error.copy()
            paged_error['y'] = range(len(paged_error))
    
            y_map = {champ: i for i, champ in enumerate(paged_error['champ'])}
            paged_sig = filtered_sig[filtered_sig['champ'].isin(paged_error['champ'])].copy()
            paged_sig['y'] = paged_sig['champ'].map(y_map)
    
            mid_fig = make_figure(paged_sig, paged_error, sort=sort_method)
            st.plotly_chart(mid_fig)
    with tab4:
        selected_classes = class_filter_ui('bot')
        filtered_error, filtered_sig = filter_by_class(role_error['Bot'], role_sig['Bot'], selected_classes)
        
        if len(filtered_error) == 0:
            st.info('No champions match the selected classes.')
        else:
            page_key = 'page_bot'
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
    
            paged_error = pagination_ui(filtered_error, page_key)
    
            paged_error = paged_error.copy()
            paged_error['y'] = range(len(paged_error))
    
            y_map = {champ: i for i, champ in enumerate(paged_error['champ'])}
            paged_sig = filtered_sig[filtered_sig['champ'].isin(paged_error['champ'])].copy()
            paged_sig['y'] = paged_sig['champ'].map(y_map)
    
            bot_fig = make_figure(paged_sig, paged_error, sort=sort_method)
            st.plotly_chart(bot_fig)
    with tab5:
        selected_classes = class_filter_ui('sup')
        filtered_error, filtered_sig = filter_by_class(role_error['Support'], role_sig['Support'], selected_classes)
        
        if len(filtered_error) == 0:
            st.info('No champions match the selected classes.')
        else:
            page_key = 'page_sup'
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
    
            paged_error = pagination_ui(filtered_error, page_key)
    
            paged_error = paged_error.copy()
            paged_error['y'] = range(len(paged_error))
    
            y_map = {champ: i for i, champ in enumerate(paged_error['champ'])}
            paged_sig = filtered_sig[filtered_sig['champ'].isin(paged_error['champ'])].copy()
            paged_sig['y'] = paged_sig['champ'].map(y_map)
    
            sup_fig = make_figure(paged_sig, paged_error, sort=sort_method)
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
            'Top': role_error['Top']['champ'].sort_values().tolist(), 
            'Jungle': role_error['Jungle']['champ'].sort_values().tolist(), 
            'Mid': role_error['Mid']['champ'].sort_values().tolist(), 
            'Bot': role_error['Bot']['champ'].sort_values().tolist(), 
            'Support': role_error['Support']['champ'].sort_values().tolist()
        }
        
        selected_role = st.session_state.get('role', 'Top')
        role_champs = champ_lists[selected_role]

        cols = st.columns(5)
        for col, role in zip(cols, roles):
            with col:
                is_active = role == selected_role
                border = '2px solid #2951f2' if is_active else '2px solid transparent'
                bg = '#172c43' if is_active else 'transparent'
                st.markdown(
                    f'''<div style="text-align: center; border: {border}; background-color: {bg}; border-radius: 8px; padding: 4px;">
                        <img src="{role_urls[role]}" width="40"/>
                    </div>''',
                    unsafe_allow_html=True
                )
                if st.button(role, use_container_width=True, key=f'role_{role}'):
                    st.session_state['role'] = role
                    st.session_state['chosen_champions'] = [role_champs[0]]
                    st.rerun()
    
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
            'Win rate threshold',
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
        threat_opps = threats.loc[:,'opp'].tolist()
    
        # --- coverage helpers ---
        def get_wr(champ, opp):
            key = f'{champ}_{opp}'
            match = full_df[full_df.iloc[:, 0] == key]
            if len(match) > 0:
                return match.iloc[0]['wr_corrected']
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
    
        def score_candidate(e, uncovered, uncovered_totals, full_df, threshold, total_threat_weight):
            covered_weight = 0
            tiebreak = 0
            for opp, total in zip(uncovered, uncovered_totals):
                wr = get_wr(e, opp)
                if wr > threshold:
                    covered_weight += total
                    tiebreak += (wr - threshold) * total
            pct_gain = covered_weight / total_threat_weight if total_threat_weight > 0 else 0
            return covered_weight, tiebreak, pct_gain
    
        # --- compute coverage state ---
        chosen = st.session_state['chosen_champions']
        coverage = get_coverage(chosen, threat_opps)
        uncovered = []
        uncovered_totals = []
        for opp in threat_opps:
            if coverage[opp]['best_wr'] <= threshold:
                uncovered.append(opp)
                uncovered_totals.append(threats.loc[threats['opp'] == opp, 'total'].values[0])
        
        total_threat_weight = threats['total'].sum()

        covered_weight = sum(
            threats.loc[threats['opp'] == opp, 'total'].values[0]
            for opp in threat_opps
            if coverage[opp]['best_wr'] > threshold
        )
        weighted_pct = covered_weight / total_threat_weight if total_threat_weight > 0 else 0
    
        # --- layout ---
        left, right = st.columns([1, 3])
    
        with left:
            # selected champ icon
            st.markdown(
                f'<div style="text-align: center;"><img src="{get_icon_url(selected_champ)}" width="80"/></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="text-align: left; font-size: 14px; ">Weighted matchup coverage: {weighted_pct*100:.0f}%</div>',
                unsafe_allow_html=True
            )
            st.markdown(progress_bar(weighted_pct, color='#26b000',  show_tooltip=False), unsafe_allow_html=True)
    
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
            if len(chosen) < 4:
                st.markdown('**Recommended backups:**')
                candidates = get_candidates(chosen, selected_champ, full_df)
                scored = []
                for e in candidates:
                    count, tiebreak, pct_gain = score_candidate(e, uncovered, uncovered_totals, full_df, threshold, total_threat_weight)
                    scored.append((e, count, tiebreak, pct_gain))
                scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
                top5 = scored[:5]
    
                for e, count, _, pct_gain in top5:
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
                        st.markdown(f'+{pct_gain*100:.0f}% coverage')
                
                new_champ = st.selectbox(
                    'Add a champion',
                    options=[nam for nam in role_champs if nam not in [selected_champ]+chosen],
                    key='new_champ'
                )
                if st.button('Add', key=f'add2_{new_champ}'):
                    st.session_state['chosen_champions'].append(new_champ)
                    st.rerun()              
            else:
                st.info('Coverage set is full.') 
           
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
            6. Continue adding champions (up to 3), or enter your own champion to see how it performs
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
At each step the tool recommends the backup champion that adds the most coverage to your remaining uncovered threats. Coverage is determined by having a greater win rate than the user-selected threshold. Once a threat is covered by a champion in your set, the algorithm continues to suggest the next champ that will cover the most remaining uncovered threats.
While the tool will recommend a set of champs that increases the coverage as much as possible, League of Legends is a game and is meant to be fun! Everyone should play the champs that they enjoy, so you are able to select your own champs to add to the "dominator set" and see how they may improve the coverage of your threat set. 
""")
