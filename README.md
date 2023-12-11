# FinalLeagueProject
This project uses the Riot Games API to retrieve and display information about a player's recent League of Legends matches.

## Overview

The application fetches match details, including game duration, kills, deaths, assists, gold earned, minions killed, damage dealt to champions, and vision score. The data is presented in a user-friendly table format using Streamlit.

## How it Works

1. The application prompts the user to enter a League of Legends player name, select the number of recent matches to analyze, and choose the region.
2. It queries the Riot Games API to obtain the match history for the specified player.
3. For each match, it extracts relevant information such as game duration, player stats, and more.
4. The collected data is displayed in a table format using the Streamlit library.

## How to Run

1. Install the required Python packages:

   ```bash
   pip install -r requirements.txt

2. Create a .env file with your RIOT_API_Key

3. Type the following into your venv terminal
   ```bash
   streamlit run riot_app.py