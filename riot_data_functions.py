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


def display_match_details(match_data):
    # You can customize this function based on how you want to display match details
    # For now, it's just showing a JSON representation
    st.json(match_data)


def calculate_kda(kills, deaths, assists):
    deaths = max(deaths, 1)  # To avoid division by zero
    return (kills + assists) / deaths


def fetch_match_data(lol_watcher, player_routing, summoner, num_matches_data):
    match_history = lol_watcher.match.matchlist_by_puuid(
        region=player_routing, puuid=summoner['puuid'], queue=420, start=0, count=num_matches_data
    )

    # Create an empty DataFrame to store the data
    data = {
        'Match ID': [],
        'Date Played': [],
        'Game Time': [],
        'Kills': [],
        'Deaths': [],
        'Assists': [],
        'KDA': [],
        'Gold Earned': [],
        'CS (Minions Killed)': [],
        'Damage Dealt to Champions': [],
        'Vision Score': [],
        'Result': [],
        'Summoner Icon': [],
        'Game Mode': [],
        'wardsPlaced': [],
        'wardsKilled': [],
        'visionWardsBoughtInGame': [],
        'visionScorePerMinute': []
    }

    for i, match_reference in enumerate(match_history, start=1):
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

                # Determine the result of the game (Win/Loss)
                result = "Win" if participant_data.get('win', False) else "Loss"

                # Calculate KDA
                try:
                    kda = calculate_kda(participant_data.get('kills', 0),
                                        participant_data.get('deaths', 0),
                                        participant_data.get('assists', 0))
                except Exception as e:
                    st.error(f"Error calculating KDA for Match ID {match_id}: {str(e)}")
                    kda = None

                # Append the data to the DataFrame
                data['Match ID'].append(i)
                data['Date Played'].append(date_played)
                data['Game Time'].append(f"{game_time_minutes}m {game_time_seconds}s")
                data['Result'].append(result)
                data['Kills'].append(participant_data.get('kills', 0))
                data['Deaths'].append(participant_data.get('deaths', 0))
                data['Assists'].append(participant_data.get('assists', 0))
                data['KDA'].append(kda)
                data['Gold Earned'].append(participant_data.get('goldEarned', 0))
                data['CS (Minions Killed)'].append(participant_data.get('totalMinionsKilled', 0))
                data['Damage Dealt to Champions'].append(participant_data.get('totalDamageDealtToChampions', 0))
                data['Vision Score'].append(participant_data.get('visionScore', 0))
                data['Game Mode'].append(match_data['info']['gameMode'])
                data['wardsPlaced'].append(participant_data.get('wardsPlaced', 0))
                data['wardsKilled'].append(participant_data.get('wardsKilled', 0))
                data['visionWardsBoughtInGame'].append(participant_data.get('visionWardsBoughtInGame', 0))

    # Make sure all lists have the same length
    length = len(data['Match ID'])
    for key in data:
        if len(data[key]) != length:
            data[key].extend([None] * (length - len(data[key])))

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    return df
