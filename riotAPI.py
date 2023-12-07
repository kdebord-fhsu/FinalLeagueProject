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


def main():
    st.set_page_config(page_title="LoL Match Information", page_icon="🎮", layout="wide")

    st.title("League of Legends Match Information")

    # PLAYER PARAMETERS
    player_name = st.text_input("Enter player name:", 'Sett on me Yuumi')
    num_matches_data = st.slider("Number of Matches", 1, 10, 5)
    player_region = st.selectbox("Select region", ['NA1', 'EUW1', 'EUN1'])
    player_routing = 'americas'  # Change as needed

    try:
        lol_watcher = setup_env()
        summoner = lol_watcher.summoner.by_name(player_region, player_name)
        match_history = lol_watcher.match.matchlist_by_puuid(
            region=player_routing, puuid=summoner['puuid'], queue=420, start=0, count=num_matches_data
        )

        # Create an empty DataFrame to store the data
        data = {'Match ID': [], 'Date Played': [], 'Game Time': [], 'Win/Loss': [], 'Kills': [], 'Deaths': [],
                'Assists': [], 'Gold Earned': [], 'CS (Minions Killed)': [], 'Damage Dealt to Champions': [],
                'Vision Score': []}

        with st.spinner("Fetching data..."):
            st.subheader('Game Information:')
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

                    # Extracting participant data for the summoner
                    participant_data = next(
                        (participant for participant in match_data['info']['participants'] if
                         participant['puuid'] == summoner['puuid']), None)

                    if participant_data:
                        # Convert timestamp to a user-friendly date format
                        date_played = pd.to_datetime(match_data['info']['gameCreation'], unit='ms').strftime(
                            '%B %d, %Y %H:%M')

                        # Determine Win/Loss
                        win_loss = "Win" if participant_data.get('win', False) else "Loss"

                        # Append the data to the DataFrame
                        data['Match ID'].append(match_id)
                        data['Date Played'].append(date_played)
                        data['Game Time'].append(f"{game_time_minutes}m {game_time_seconds}s")
                        data['Win/Loss'].append(win_loss)
                        data['Kills'].append(participant_data.get('kills', 0))
                        data['Deaths'].append(participant_data.get('deaths', 0))
                        data['Assists'].append(participant_data.get('assists', 0))
                        data['Gold Earned'].append(participant_data.get('goldEarned', 0))
                        data['CS (Minions Killed)'].append(participant_data.get('totalMinionsKilled', 0))
                        data['Damage Dealt to Champions'].append(
                            participant_data.get('totalDamageDealtToChampions', 0))
                        data['Vision Score'].append(participant_data.get('visionScore', 0))
                    else:
                        st.warning(f"No participant data found for Match ID: {match_id}")
                else:
                    st.warning("Match ID not found in the match reference.")

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)

        # Display the DataFrame in Streamlit
        st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
