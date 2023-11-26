from riotwatcher import LolWatcher
from dotenv import load_dotenv
import streamlit as st
import os

def setup_env():
    api_key = "RGAPI-45c2a3ef-2d6f-4df7-995d-b324c08f2a0f"
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

                st.write(f"Match Reference Structure: {type(match_reference)} - {match_reference}")

                if match_id:
                    match_data = lol_watcher.match.by_id(region=player_routing, match_id=match_id)
                    game_time_minutes = match_data['info']['gameDuration'] // 60
                    game_time_seconds = match_data['info']['gameDuration'] % 60

                    st.write(f"Match ID: {match_id}")
                    st.write(f"Game Time: {game_time_minutes}m {game_time_seconds}s")

                    for participant in match_data['info']['participants']:
                        st.write(
                            f"Participant ID: {participant['participantId']}, Gold Earned: {participant['goldEarned']}")
                else:
                    st.warning("Match ID not found in the match reference.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
