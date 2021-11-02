import pandas as pd
import numpy as np
import streamlit as st


fbref_file1='https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats'
fbref_file2='https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats'
fbref_file3='https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats'
fbref_file4='https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats'

st.set_page_config(
     page_title="",
     layout="wide",
     )

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
    "Filter by league:", leagues, index=1)

data=data.loc[(data['Comp'] == league_choice)]


teams = list(data['Squad'].drop_duplicates())
teams=sorted(teams)
teams_choice = st.sidebar.selectbox(
    "Filter by Team:", teams, index=0)

data=data.loc[(data['Squad'] == teams_choice)]

mins_choice = st.sidebar.number_input(
    'Filter by Minimum 90s played:',step=0.5)

data = data[data['90s'] > mins_choice]

metrics=data.columns.tolist()#["Gls","Sh/90","SoT/90","CrdY","Fls/90","Tkl/90"]
metrics.remove("Comp")
metrics.remove("Player")
metrics.remove("Squad")

choose_metric = st.sidebar.selectbox(
    "Sort by:", metrics, index=0)
choose_metric = ''.join(choose_metric)

data = data.sort_values(by=[choose_metric],ascending=False)


data=data[["Player","Squad","MP","90s","Gls","Gls/90","Sh/90","SoT/90","CrdY",
           "CrdR","Bookings","Fls","Fls/90","Tkl","Tkl/90"]]
# Main
st.title(f"Toolkit Builder")

# Main - dataframes
st.markdown("### Selected Team's Stats 2020/21")

st.dataframe(data.sort_values(by=[choose_metric],ascending=False).reset_index(drop=True))
