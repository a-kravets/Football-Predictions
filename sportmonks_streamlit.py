#Load in Statsbomb competition and match data
#This is a library for loading json files.
#import json
import pandas as pd
from pandas import json_normalize
import matplotlib.pyplot as plt
import streamlit as st
#import altair as alt
import requests
import datetime as dt


st.set_page_config(
    page_title="Football match predictions",
    page_icon=":soccer",
    #layout="wide",
    #initial_sidebar_state="expanded",
    )

#We'll hide menu burgerand footer, and add our content in the bottom
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
            	content:'Made with love and Streamlit'; 
            	visibility: visible;
            	display: block;
            	position: relative;
            	#background-color: red;
            	padding: 5px;
            	top: 2px;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.title("Football match predictions made easy")
st.header("Check the matches probabilities for the next 7 days")

API_TOKEN = ENV['API_TOKEN']


# Load all the leagues SportMonks offers in its free plan
leagues = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues?api_token="+API_TOKEN+"&include=country")
leagues = leagues.json()

# Get all the leagues and save country ids & names and leagues ids
country_ids = []
league_ids = []
league_names = []
country_league = ['------Select a league------']
for league in leagues['data']:
    if league['id'] not in league_ids:
        country_ids.append(league['country_id'])
        league_ids.append(league['id'])
        league_names.append(league['name'])
        country_league.append(league['country']['data']['name'] + " " + league['name'] + " (" + str(league['id']) + ")")
    #print(league['id'], league['name'], league['country_id'])
    

# Select menu
add_selectbox_league = st.selectbox(
    "What football league are interested in?",
    (country_league)
)        


if add_selectbox_league != '------Select a league------':

    selected_league = add_selectbox_league
    
    # Get the league id from the list
    selected_league = selected_league.split()
    selected_league = selected_league[-1]
    selected_league = selected_league[1:-1]
    
    # Load all the matches that will take place in the next 7 days in the chosen league
    today = dt.date.today().strftime("%Y-%m-%d")
    days = dt.date.today() + dt.timedelta(days=7)
    
    
    fixtures = requests.get("https://soccer.sportmonks.com/api/v2.0/fixtures/between/"+str(today)+"/"+str(days)+"?api_token="+API_TOKEN+"&leagues="+selected_league+"&include=localTeam,visitorTeam")
    
    fixtures = fixtures.json()
    
    # Looping and saving fixture details with id's to display in a select menu
    fixtures_all = ['------Select a match------']
    for i in fixtures['data']:
        localteam_id = i['localteam_id']
        visitorteam_id = i['visitorteam_id']
        fixtures_all.append(str(i['time']['starting_at']['date'])+ " " + str(i['time']['starting_at']['time'])+ " " +\
              str(i['localTeam']['data']['name'])+ " vs "+str(i['visitorTeam']['data']['name'])+ " ("+str(i['id'])+")")
        #print(str(i['time']['starting_at']['date'])+ " " + str(i['time']['starting_at']['time'])+ " " +\
              #str(i['localTeam']['data']['name'])+ " vs "+str(i['visitorTeam']['data']['name'])+ " ("+str(i['id'])+")")
    
    
    # Select menu
    add_selectbox_fixture = st.selectbox(
        "What match are interested in?",
        (fixtures_all)
    )        
    
    if add_selectbox_fixture != '------Select a match------':
    
        selected_fixture = add_selectbox_fixture
        
        # Get the fixture id from the list
        selected_fixture = selected_fixture.split()
        selected_fixture = selected_fixture[-1]
        selected_fixture = selected_fixture[1:-1]
        
        
        # Load probabilities
        probabilities = requests.get("https://soccer.sportmonks.com/api/v2.0/predictions/probabilities/fixture/"\
                                     +str(selected_fixture)+"?api_token="+API_TOKEN+"&include=fixture.localTeam,fixture.visitorTeam")
        
        probabilities = probabilities.json()
        
        # Leave only data (filtering out meta part)
        probabilities = probabilities['data']
        
        localTeam = probabilities['fixture']['data']['localTeam']['data']['name']
        visitorTeam = probabilities['fixture']['data']['visitorTeam']['data']['name']
        
        st.text(localTeam + ' Wins has a probability of ' + str(probabilities['predictions']['home']) + "%")
        st.text(visitorTeam + ' Wins has a probability of ' + str(probabilities['predictions']['away']) + "%")
        st.text('Draw has a probability of ' + str(probabilities['predictions']['draw']) + "%")
        
        st.text('Both Teams To Score Probability: ' + str(probabilities['predictions']['btts']) + "%")
        
        st.text(localTeam + ' Over 0.5 has a probability of ' + str(probabilities['predictions']['HT_over_0_5']) + "%")
        st.text(visitorTeam + ' Over 0.5 has a probability of ' + str(probabilities['predictions']['AT_over_0_5']) + "%")
        st.text(localTeam + ' Under 0.5 has a probability of ' + str(probabilities['predictions']['HT_under_0_5']) + "%")
        st.text(visitorTeam + ' Under 0.5 has a probability of ' + str(probabilities['predictions']['AT_under_0_5']) + "%")
        
        st.text(localTeam + ' Over 1.5 has a probability of ' + str(probabilities['predictions']['HT_over_1_5']) + "%")
        st.text(visitorTeam + ' Over 1.5 has a probability of ' + str(probabilities['predictions']['AT_over_1_5']) + "%")
        st.text(localTeam + ' Under 1.5 has a probability of ' + str(probabilities['predictions']['HT_under_1_5']) + "%")
        st.text(visitorTeam + ' Under 1.5 has a probability of ' + str(probabilities['predictions']['AT_under_1_5']) + "%")
        
        st.text('Over 2.5 has a probability of ' + str(probabilities['predictions']['over_2_5']) + "%")
        st.text('Under 2.5 has a probability of ' + str(probabilities['predictions']['under_2_5']) + "%")
        
        st.text('Over 3.5 has a probability of ' + str(probabilities['predictions']['over_3_5']) + "%")
        st.text('Under 3.5 has a probability of ' + str(probabilities['predictions']['under_3_5']) + "%")
        
        st.text('Score probabilities for ' + localTeam + ' vs ' + visitorTeam)
        for score, probability in probabilities['predictions']['correct_score'].items():
            st.text("Score " + str(score) + " has a probability of " + str(probability) + "%")
        
        # We can sort scores porbabilities by it's value and visualize it graphically
        #dict(sorted(x.items(), key=lambda item: item[1]))
        
        
    








