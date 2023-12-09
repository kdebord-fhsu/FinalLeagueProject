from riotwatcher import LolWatcher
from dotenv import load_dotenv
import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

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



def main():
    # Set Streamlit page configuration
    st.set_page_config(page_title="LoL Match Information", page_icon="🎮", layout="wide")

    # Display main title
    st.title("League of Legends Match Information")

    # Get player parameters from user input
    player_name = st.text_input("Enter player name:", 'Sett on me Yuumi')
    num_matches_data = st.slider("Number of Matches", 1, 20, 5)
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
                    expander_title = f"Game Mode: {row['Game Mode']} - Result: {row['Result']}"
                    with st.expander(expander_title):
                        result_color = 'green' if row['Result'] == 'Win' else 'red'

                        # Format gold earned with commas
                        gold_earned_formatted = "{:,}".format(row['Gold Earned'])

                        # Format damage dealt to champions with commas
                        damage_to_champions_formatted = "{:,}".format(row['Damage Dealt to Champions'])

                        st.write(f"KDA: <span style='color:{result_color}'>{row['KDA']:.2f}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Kills: <span style='color:{result_color}'>{row['Kills']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Deaths: <span style='color:{result_color}'>{row['Deaths']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Assists: <span style='color:{result_color}'>{row['Assists']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Gold Earned: <span style='color:{result_color}'>{gold_earned_formatted}</span>",
                                 unsafe_allow_html=True)
                        st.write(
                            f"CS (Minions Killed): <span style='color:{result_color}'>{row['CS (Minions Killed)']}</span>",
                            unsafe_allow_html=True)
                        st.write(
                            f"Damage Dealt to Champions: <span style='color:{result_color}'>{damage_to_champions_formatted}</span>",
                            unsafe_allow_html=True)
                        st.write(f"Vision Score: <span style='color:{result_color}'>{row['Vision Score']}</span>",
                                 unsafe_allow_html=True)
                        st.write(f"Warding: <span style='color:{result_color}'>{row['wardsPlaced']} placed </span>, "
                                 f"<span style='color:{result_color}'>{row['wardsKilled']} killed</span>" ,
                                 unsafe_allow_html=True)
                        st.write(
                            f"Vision Wards Bought: <span style='color:{result_color}'>{row['visionWardsBoughtInGame']}</span>",
                            unsafe_allow_html=True)

                        # Extracting gold earned data for each match
                        gold_earned = df['Gold Earned'].astype(int).tolist()

                        # Calculate the absolute difference in gold earned between consecutive matches
                        gold_earned_diff = [abs(gold_earned[i] - gold_earned[i - 1]) for i in
                                            range(1, len(gold_earned))]
                        # Create subplots for gold earned difference and KDA/vision score
                        if gold_earned_diff and df['KDA'].notna().all() and df['Vision Score'].notna().all():
                            fig, (ax_gold, ax_kda_vs) = plt.subplots(1, 2, figsize=(12, 4))

                            # Gold earned difference subplot
                            ax_gold.plot(range(1, len(gold_earned_diff) + 1), gold_earned_diff, marker='o',
                                         linestyle='-', color='gold')
                            ax_gold.set_title('Gold Earned Difference Between Matches')
                            ax_gold.set_ylim(0, max(gold_earned_diff))
                            ax_gold.set_xlabel('Match Index')
                            ax_gold.set_ylabel('Gold Earned Difference')

                            # KDA and vision score subplot
                            ax_kda_vs.plot(range(1, len(df['KDA']) + 1), df['KDA'], marker='o', linestyle='-',
                                           color='blue', label='KDA')
                            ax_kda_vs.plot(range(1, len(df['Vision Score']) + 1), df['Vision Score'], marker='o',
                                           linestyle='-', color='green', label='Vision Score')
                            ax_kda_vs.set_title('KDA and Vision Score Between Matches')
                            ax_kda_vs.set_ylim(0, max(max(df['KDA']), max(df['Vision Score'])))
                            ax_kda_vs.set_xlabel('Match Index')
                            ax_kda_vs.set_ylabel('Value')
                            ax_kda_vs.legend()

                            # Adjust layout to prevent overlap
                            plt.tight_layout()

                            # Show the subplots
                            st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()