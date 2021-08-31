
import pandas as pd
import numpy as np
import streamlit as st
#import matplotlib.pyplot as plt


fbref_file1='https://fbref.com/en/comps/Big5/2020-2021/stats/players/2020-2021-Big-5-European-Leagues-Stats'
fbref_file2='https://fbref.com/en/comps/Big5/2020-2021/shooting/players/2020-2021-Big-5-European-Leagues-Stats'
fbref_file3='https://fbref.com/en/comps/Big5/2020-2021/misc/players/2020-2021-Big-5-European-Leagues-Stats'
fbref_file4='https://fbref.com/en/comps/Big5/2020-2021/defense/players/2020-2021-Big-5-European-Leagues-Stats'

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
df["Sh/90"] = pd.to_numeric(df["Sh/90"])
df["SoT/90"] = pd.to_numeric(df["SoT/90"])

df["Player+Team"]=df["Player"]+" "+df["Squad"]

dfatt=df.join(af.set_index('Player+Team'), on='Player+Team')


df1=get_data(fbref_file3)
df1["90s"] = pd.to_numeric(df1["90s"])
df1["Fls"] = pd.to_numeric(df1["Fls"])
df1["CrdY"] = pd.to_numeric(df1["CrdY"])

df1["Fls/90"]=(df1["Fls"]/df1["90s"]).round(2)
df1["Player+Team"]=df1["Player"]+" "+df1["Squad"]

cols1= ["Player+Team","Comp","CrdY","Fls","Fls/90"] #,"Squad","90s"

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

dfdef=dfdef[["Player+Team","Comp","Player","Squad","MP","90s","CrdY","Fls","Fls/90","Tkl","Tkl/90"]]
dfatt=dfatt[["Player+Team","Gls","Sh/90","SoT/90"]]

data=dfatt.join(dfdef.set_index('Player+Team'), on='Player+Team')

data=data[["Comp","Player","Squad","MP","90s","Gls","Sh/90","SoT/90","CrdY","Fls","Fls/90","Tkl","Tkl/90"]]

# App

# Sidebar - title & filters
st.sidebar.markdown('### Data Filters')

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



data=data[["Player","Squad","MP","90s","Gls","Sh/90","SoT/90","CrdY","Fls","Fls/90","Tkl","Tkl/90"]]
# Main
st.title(f"Toolkit Builder")

# Main - dataframes
st.markdown("### Selected Team's Stats 2020/21")

data=data.sort_values(by=["Gls"],ascending=False).reset_index(drop=True)

st.dataframe(data.style.format({"90s":"{:.2f}","Sh/90":"{:.2f}","SoT/90":"{:.2f}"
                                ,"Fls/90":"{:.2f}","Tkl":"{:.2f}","Tkl/90":"{:.2f}"}))
