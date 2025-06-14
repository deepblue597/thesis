#%% 

import plotly.graph_objects as go 
import pandas as pd
from plotly.subplots import make_subplots

# %%
df = pd.read_csv('data/2010SantaBarbaraCA.csv')
# %%
df 
# %%
#df['LST_TIME'] = pd.to_numeric(df['LST_TIME'], errors='coerce')
data = [ go.Heatmap(
    x = df['DAY'], 
    y = df['LST_TIME'] , 
    z = df['T_HR_AVG'], 
    colorscale='Jet'
)]
layout = go.Layout(
    yaxis= dict(
        autorange = 'reversed'
    )
)
# %%
fig = go.Figure(data = data , layout=layout) 
 
# %%
fig.show()
# %% mulitple heatmaps in the same figure 

df1 = pd.read_csv('data/2010SitkaAK.csv')
df2 = pd.read_csv('data/2010SantaBarbaraCA.csv')
df3 = pd.read_csv('data/2010YumaAZ.csv')


# %%
# we put zmin and zmax so that the heatmaps are consistent with each other 
trace1 =  go.Heatmap(
    x = df1['DAY'], 
    y = df1['LST_TIME'] , 
    z = df1['T_HR_AVG'], 
    colorscale='Jet', 
    zmin= 0 , 
    zmax= 40 
)

trace2 =  go.Heatmap(
    x = df2['DAY'], 
    y = df2['LST_TIME'] , 
    z = df2['T_HR_AVG'], 
    colorscale='Jet', 
    zmin= 0 , 
    zmax= 40 
)

trace3 =  go.Heatmap(
    x = df3['DAY'], 
    y = df3['LST_TIME'] , 
    z = df3['T_HR_AVG'], 
    colorscale='Jet', 
    zmin= 0 , 
    zmax= 40 
)
# %%

fig  = make_subplots(
    rows = 1, 
    cols = 3, 
    subplot_titles=[ 'Sitka, AK','Santa Barbara, CA', 'Yuma, AZ'], 
    shared_yaxes= True 
)
# %%
# here we dont create a layout component but we use update layout 
# because we have subplots 
# use add trace which is a newer method than append 
fig.update_layout(
    yaxis= dict(
        autorange = 'reversed'
    )
)
fig.append_trace(
    trace1, 
     1, 
     1
)

fig.add_trace(
    trace2, 
     1, 
     2
)

fig.append_trace(
    trace3, 
     1, 
    3
)
fig.show()
# %%
