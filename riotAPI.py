from riotwatcher import LolWatcher
from dotenv import load_dotenv
import streamlit as st
import os
import pandas as pd

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")


def setup_env():
    api_key = RIOT_API_KEY
    lol_watcher = LolWatcher(api_key)
    return lol_watcher


def get_summoner_icon_url(summoner_id, lol_watcher):
    summoner_data = lol_watcher.summoner.by_id(region='na1', encrypted_summoner_id=summoner_id)
    profile_icon_id = summoner_data['profileIconId']
    return f"http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/{profile_icon_id}.png"


def display_match_details(match_data):
    # You can customize this function based on how you want to display match details
    # For now, it's just showing a JSON representation
    st.json(match_data)


def fetch_match_data(lol_watcher, player_routing, summoner, num_matches_data):
    match_history = lol_watcher.match.matchlist_by_puuid(
        region=player_routing, puuid=summoner['puuid'], queue=420, start=0, count=num_matches_data
    )

    # Create an empty DataFrame to store the data
    data = {'Match ID': [], 'Date Played': [], 'Game Time': [], 'Kills': [], 'Deaths': [], 'Assists': [],
            'Gold Earned': [], 'CS (Minions Killed)': [], 'Damage Dealt to Champions': [], 'Vision Score': [],
            'Result': [], 'Summoner Icon': []}

    for match_reference in match_history:
        if isinstance(match_reference, str):
            match_id = match_reference
        elif isinstance(match_reference, dict):
            match_id = match_reference.get('gameId')
        else:
            st.warning(f"Invalid match reference structure: {match_reference}")
            continue

        if match_id:
            match_data = lol_watcher.match.by_id(region=player_routing, match_id=match_id)

            game_time_minutes = match_data['info']['gameDuration'] // 60
            game_time_seconds = match_data['info']['gameDuration'] % 60

            # Extracting player stats for the first participant (assuming it's the player we are querying)
            participants = match_data['info']['participants']
            participant_data = next((p for p in participants if p.get('summonerId') == summoner['id']), None)

            if participant_data:
                # Convert timestamp to a user-friendly date format
                date_played = pd.to_datetime(match_data['info']['gameCreation'], unit='ms').strftime('%B %d, %Y %H:%M')

                # Fetch summoner icon URL
                summoner_icon_url = get_summoner_icon_url(summoner['id'], lol_watcher)

                # Determine the result of the game (Win/Loss)
                result = "Win" if participant_data.get('win', False) else "Loss"

                # Append the data to the DataFrame
                data['Match ID'].append(match_id)
                data['Date Played'].append(date_played)
                data['Game Time'].append(f"{game_time_minutes}m {game_time_seconds}s")
                data['Result'].append(result)
                data['Kills'].append(participant_data.get('kills', 0))
                data['Deaths'].append(participant_data.get('deaths', 0))
                data['Assists'].append(participant_data.get('assists', 0))
                data['Gold Earned'].append(participant_data.get('goldEarned', 0))
                data['CS (Minions Killed)'].append(participant_data.get('totalMinionsKilled', 0))
                data['Damage Dealt to Champions'].append(participant_data.get('totalDamageDealtToChampions', 0))
                data['Vision Score'].append(participant_data.get('visionScore', 0))
                data['Summoner Icon'].append(summoner_icon_url)

                # Make sure all lists have the same length
                length = len(data['Match ID'])
                for key in data:
                    if len(data[key]) != length:
                        data[key].extend([None] * (length - len(data[key])))
            else:
                st.warning(f"No valid participant data found for Match ID: {match_id}")

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    return df


def main():
    # Set Streamlit page configuration
    st.set_page_config(page_title="LoL Match Information", page_icon="🎮", layout="wide")

    # Display main title
    st.title("League of Legends Match Information")

    # Get player parameters from user input
    player_name = st.text_input("Enter player name:", 'Sett on me Yuumi')
    num_matches_data = st.slider("Number of Matches", 1, 10, 5)
    player_region = st.selectbox("Select region", ['NA1', 'EUW1', 'EUN1'])
    player_routing = 'americas'  # Change as needed

    try:
        # Set up Riot API environment
        lol_watcher = setup_env()
        summoner = lol_watcher.summoner.by_name(player_region, player_name)

        with st.spinner("Fetching data..."):
            # Fetch match data
            df = fetch_match_data(lol_watcher, player_routing, summoner, num_matches_data)

            # Display match details for each match
            for _, row in df.iterrows():
                # Create a column for each match
                col1, col2 = st.columns(2)

                with col1:
                    # Display basic match information
                    result_color = 'green' if row['Result'] == 'Win' else 'red'
                    st.write(f"Date Played: <span style='color:{result_color}'>{row['Date Played']}</span>",
                             unsafe_allow_html=True)
                    st.write(f"Game Time: <span style='color:{result_color}'>{row['Game Time']}</span>",
                             unsafe_allow_html=True)

                with col2:
                    # Display details and statistics inside the expander
                    expander_title = f"Match ID: {row['Match ID']} - Result: {row['Result']}"
                    with st.expander(expander_title):
                        result_color = 'green' if row['Result'] == 'Win' else 'red'
                        st.write(f"Kills: <span style='color:{result_color}'>{row['Kills']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Deaths: <span style='color:{result_color}'>{row['Deaths']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Assists: <span style='color:{result_color}'>{row['Assists']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Gold Earned: <span style='color:{result_color}'>{row['Gold Earned']}</span>",
                                 unsafe_allow_html=True)
                        st.write(
                            f"CS (Minions Killed): <span style='color:{result_color}'>{row['CS (Minions Killed)']}</span>",
                            unsafe_allow_html=True)
                        st.write(
                            f"Damage Dealt to Champions: <span style='color:{result_color}'>{row['Damage Dealt to Champions']}</span>",
                            unsafe_allow_html=True)
                        st.write(f"Vision Score: <span style='color:{result_color}'>{row['Vision Score']}</span>",
                                 unsafe_allow_html=True)
                        # Add more details and statistics as needed

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
