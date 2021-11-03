import pandas as pd
import numpy as np
import streamlit as st


st.set_page_config(
     page_title="",
     layout="wide",
     )


fbref_file1='https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats'
fbref_file2='https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats'
fbref_file3='https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats'
fbref_file4='https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats'


eng1 = pd.read_csv("https://www.football-data.co.uk/mmz4281/2122/E0.csv")
eng1['League'] = 'English Premier League'
euro1=pd.read_csv("https://www.football-data.co.uk/mmz4281/2122/D1.csv")
euro1['League'] = "German Bundesliga"
euro2=pd.read_csv("https://www.football-data.co.uk/mmz4281/2122/I1.csv")
euro2['League'] = "Serie A"
euro3=pd.read_csv("https://www.football-data.co.uk/mmz4281/2122/SP1.csv")
euro3['League'] = "La Liga"
euro4=pd.read_csv("https://www.football-data.co.uk/mmz4281/2122/F1.csv")
euro4['League'] = "Ligue 1"

df2122=eng1.append([euro1,euro2,euro3,euro4])

df_goals=pd.DataFrame(data=df2122["FTHG"] + df2122["FTAG"],columns = ['TotalGoals'])
df2122 = pd.concat([df2122,df_goals], axis=1)

home_teams = df2122["HomeTeam"].unique()
away_teams = df2122["AwayTeam"].unique()
all_teams = list(set(np.append(home_teams,away_teams)))

@st.cache(allow_output_mutation=True)
def calc_over (df, team):
    
    team_goals = dict()
    
    df_team = df2122[(df2122["HomeTeam"]==team) | (df2122["AwayTeam"]==team)]
    
    team_over_1 = df_team.apply(lambda x:
                                1 if ((x["HomeTeam"] ==team and x["TotalGoals"]>=2) or
                                                  (x["AwayTeam"] == team and x["TotalGoals"]>=2))
                                else(0),axis=1).sum()
    
    team_over_2 = df_team.apply(lambda x:
                                1 if ((x["HomeTeam"] ==team and x["TotalGoals"]>=3) or
                                                  (x["AwayTeam"] == team and x["TotalGoals"]>=3))
                                else(0),axis=1).sum()
    BTTS = df_team.apply(lambda x:
                                1 if ((x["FTHG"]>0) and (x["FTAG"] >0))
                                else(0),axis=1).sum()
    goals_scored = df_team.apply(
        lambda x: x["FTHG"] if x["HomeTeam"] == team 
        else x["FTAG"], axis=1).sum()
    goals_conceded = df_team.apply(
        lambda x: x["FTAG"] if x["HomeTeam"] == team 
        else x["FTHG"], axis=1).sum()
    corners_taken = df_team.apply(
        lambda x: x["HC"] if x["HomeTeam"] == team 
        else x["AC"], axis=1).sum()
    cards_received = df_team.apply(
        lambda x: (x["HY"] + x["HR"]) if x["HomeTeam"] == team 
        else (x["AY"] + x["AR"]), axis=1).sum()
        
    games_played = df_team.apply(lambda x: 1 
    if (x["HomeTeam"] ==team)
        else (1
              if(x["AwayTeam"] == team )else 0 ),axis=1).sum()
        
    team_goals["% Over 2.5"] = round(team_over_2/games_played*100,1)
    team_goals["% Over 1.5"] = round(team_over_1/games_played*100,1)
    team_goals["% BTTS"] = round(BTTS/games_played*100,1)
    team_goals["Avg Goals For"] = round(goals_scored/games_played,1)
    team_goals["Avg Goals Against"] = round(goals_conceded/games_played,1)
    team_goals["Avg Corners Taken"] = round(corners_taken/games_played,1)
    team_goals["Avg Bookings Rec."] = round(cards_received/games_played,1)
    return team_goals

all_teams = df2122.HomeTeam.unique()
all_teams_stats =[]

for team in all_teams:
    team_stats = calc_over(df2122, team)
    all_teams_stats.append(team_stats)

df_all_stats=pd.DataFrame(all_teams_stats,index=home_teams)
df_all_stats=df_all_stats.rename_axis('Squad').reset_index()


def calc_ref (df, ref):
    
    ref_data = dict()
    
    df_refs = df2122[(df2122["Referee"]==ref)]
    
    cards=df_refs.apply(
        lambda x: (x["HY"]+x["AY"]+x["HR"]+x["AR"]) if x["Referee"] == ref
        else (0), axis=1).sum()
    home_cards=df_refs.apply(
        lambda x: (x["HY"]+x["HR"]) if x["Referee"] == ref
        else (0), axis=1).sum()
    away_cards=df_refs.apply(
        lambda x: (x["AY"]+x["AR"]) if x["Referee"] == ref
        else (0), axis=1).sum()
    fouls=df_refs.apply(
        lambda x: (x["HF"]+x["AF"]) if x["Referee"] == ref
        else (0), axis=1).sum()
    
    games_reffed = df_refs.apply(lambda x: 1 
    if (x["Referee"] ==ref)
        else (0),axis=1).sum()
    
    ref_data["Avg cards"]=round(cards/games_reffed,2)
    ref_data["Avg home cards"]=round(home_cards/games_reffed,2)
    ref_data["Avg away cards"]=round(away_cards/games_reffed,2)
    ref_data["Avg fouls awarded"]=round(fouls/games_reffed,2)
    ref_data["Cards per foul"]=ref_data["Avg cards"]/ref_data["Avg fouls awarded"]
    return ref_data

all_refs = df2122.Referee.unique()
all_refs = all_refs [:-1]
all_refs_stats =[]

for ref in all_refs:
    ref_stats = calc_ref(df2122, ref)
    all_refs_stats.append(ref_stats)

df_all_refs=pd.DataFrame(all_refs_stats,index=all_refs)
df_all_refs=df_all_refs.rename_axis('Referees').reset_index()

@st.cache(allow_output_mutation=True)
def get_data(fbref_file):
    df=pd.read_html(fbref_file)[0]
    df = df.droplevel(0, axis=1)
    df = df[df.Player != 'Player']
    return (df)

af=get_data(fbref_file1)
af["MP"] = pd.to_numeric(af["MP"])

af["Player+Team"]=af["Player"]+" "+af["Squad"]

af=af[["Player+Team","MP"]]

df=get_data(fbref_file2)
df["90s"] = pd.to_numeric(df["90s"]).round(2)
df["Gls"] = pd.to_numeric(df["Gls"])
df["Gls/90"]=(df["Gls"]/df["90s"]).round(2)
df["Sh/90"] = pd.to_numeric(df["Sh/90"])
df["SoT/90"] = pd.to_numeric(df["SoT/90"])

df["Player+Team"]=df["Player"]+" "+df["Squad"]

dfatt=df.join(af.set_index('Player+Team'), on='Player+Team')


df1=get_data(fbref_file3)
df1["90s"] = pd.to_numeric(df1["90s"])
df1["Fls"] = pd.to_numeric(df1["Fls"])
df1["CrdY"] = pd.to_numeric(df1["CrdY"])
df1["CrdR"] = pd.to_numeric(df1["CrdR"])
df1["Bookings"]=df1["CrdY"]+df1["CrdR"]

df1["Fls/90"]=(df1["Fls"]/df1["90s"]).round(2)
df1["Player+Team"]=df1["Player"]+" "+df1["Squad"]

cols1= ["Player+Team","Comp","CrdY","CrdR","Bookings","Fls","Fls/90"] #,"Squad","90s"

df1 = df1[cols1]

df2=get_data(fbref_file4)

df2.columns.values[14] = "TEST"

df2["90s"] = pd.to_numeric(df2["90s"])
df2["Tkl"] = pd.to_numeric(df2["Tkl"])

df2["Tkl/90"]=(df2["Tkl"]/df2["90s"]).round(2)
df2["Player+Team"]=df2["Player"]+" "+df2["Squad"]

cols2= ["Player+Team","Player","Squad","90s","Tkl","Tkl/90"] #

df2 = df2[cols2]

dfdef=df1.join(df2.set_index('Player+Team'), on='Player+Team')
dfdef=dfdef.join(af.set_index('Player+Team'), on='Player+Team')

dfdef=dfdef[["Player+Team","Comp","Player","Squad","MP","90s","CrdY",
             "CrdR","Bookings","Fls","Fls/90","Tkl","Tkl/90"]]
dfatt=dfatt[["Player+Team","Gls","Gls/90","Sh/90","SoT/90"]]

data=dfatt.join(dfdef.set_index('Player+Team'), on='Player+Team')

data=data[["Comp","Player","Squad","MP","90s","Gls","Gls/90","Sh/90","SoT/90","CrdY",
           "CrdR","Bookings","Fls","Fls/90","Tkl","Tkl/90"]]


# App
st.sidebar.markdown('### Data Filters')
# Sidebar - title & filters


leagues = list(data['Comp'].drop_duplicates())
league_choice = st.sidebar.selectbox(
    "Filter by league:", leagues, index=0)

data=data.loc[(data['Comp'] == league_choice)]


teams = list(data['Squad'].drop_duplicates())
teams=sorted(teams)
teams_choice = st.sidebar.selectbox(
    "Filter by Team:", teams, index=0)

data=data.loc[(data['Squad'] == teams_choice)]
df_all_stats=df_all_stats.loc[(df_all_stats['Squad'] == teams_choice)]

mins_choice = st.sidebar.number_input(
    'Filter by Minimum 90s played:',step=0.5)

data = data[data['90s'] > mins_choice]

metrics=data.columns.tolist()#["Gls","Sh/90","SoT/90","CrdY","Fls/90","Tkl/90"]
metrics.remove("Comp")
metrics.remove("Player")
metrics.remove("Squad")

choose_metric = st.sidebar.selectbox(
    "Sort by:", metrics, index=3)
choose_metric = ''.join(choose_metric)

data = data.sort_values(by=[choose_metric],ascending=False)


data=data[["Player","Squad","MP","90s","Gls","Gls/90","Sh/90","SoT/90","CrdY",
           "CrdR","Bookings","Fls","Fls/90","Tkl","Tkl/90"]]

referees = list(df2122['Referee'].drop_duplicates())
referees = referees [:-1]
ref_choice = st.sidebar.selectbox(
    "Select referee:", referees, index=0)

df_all_refs=df_all_refs.loc[(df_all_refs['Referees'] == ref_choice)]

# Main
st.title(f"Toolkit Builder")

# Main - dataframes
st.markdown("### Player Stats 2021/22")

data=data.sort_values(by=[choose_metric],ascending=False).reset_index(drop=True)

st.dataframe(data.assign(hack='').set_index('hack'))

st.markdown("### Team Stats 2021/22")

st.dataframe(df_all_stats.assign(hack='').set_index('hack'))

st.markdown("### Ref Stats 2021/22")

st.dataframe(df_all_refs.assign(hack='').set_index('hack'))
