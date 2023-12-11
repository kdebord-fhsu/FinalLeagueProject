import streamlit as st
import matplotlib.pyplot as plt
from riot_data_functions import setup_env, fetch_match_data

def plot_graph(df, selected_info):
    if not selected_info:
        st.warning("Please select at least one information to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    for info in selected_info:
        if info == 'Gold Earned':
            ax.plot(df['Match ID'], df['Gold Earned'], marker='o', linestyle='-', label='Gold Earned')
        elif info == 'KDA':
            ax.plot(df['Match ID'], df['KDA'], marker='o', linestyle='-', label='KDA')
        elif info == 'Vision Score':
            ax.plot(df['Match ID'], df['Vision Score'], marker='o', linestyle='-', label='Vision Score')
        elif info == 'Assists':
            ax.plot(df['Match ID'], df['Assists'], marker='o', linestyle='-', label='Assists')
        elif info == 'CS (Minions Killed)':
            ax.plot(df['Match ID'], df['CS (Minions Killed)'], marker='o', linestyle='-', label='CS (Minions Killed)')
        elif info == 'Deaths':
            ax.plot(df['Match ID'], df['Deaths'], marker='o', linestyle='-', label='Deaths')
        elif info == 'Damage Dealt to Champions':
            ax.plot(df['Match ID'], df['Damage Dealt to Champions'], marker='o', linestyle='-', label='Damage Dealt to Champions')
        elif info == 'wardsPlaced':
            ax.plot(df['Match ID'], df['wardsPlaced'], marker='o', linestyle='-', label='Wards Placed')
        elif info == 'wardsKilled':
            ax.plot(df['Match ID'], df['wardsKilled'], marker='o', linestyle='-', label='Wards Killed')
        elif info == 'visionWardsBoughtInGame':
            ax.plot(df['Match ID'], df['visionWardsBoughtInGame'], marker='o', linestyle='-', label='Vision Wards Bought')
        elif info == 'Vision Score':
            ax.plot(df['Match ID'], df['Vision Score'], marker='o', linestyle='-', label='Vision Score')
        elif info == 'Kills':
            ax.plot(df['Match ID'], df['Kills'], marker='o', linestyle='-', label='Kills')

    ax.set_title('Selected Information Between Matches')
    ax.set_xlabel('Match Index')
    ax.set_ylabel('Value')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)


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

                        # Get numeric columns excluding 'Match ID' for the multiselect options
                        numeric_columns = df.drop(columns=['Match ID']).select_dtypes(include=['number']).columns

                        # Display the multiselect widget for selecting information to plot
                        selected_info = st.multiselect("Select information to plot",
                                                       numeric_columns,
                                                       key=f"{row['Match ID']}_multiselect")

                        # Display the graph based on user's selection
                        plot_graph(df, selected_info)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()