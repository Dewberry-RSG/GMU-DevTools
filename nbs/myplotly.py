from plotly import __version__
import numpy as np 
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#print(__version__) # requires version >= 1.9.0
init_notebook_mode(connected=True)
import plotly.plotly as py
import plotly.graph_objs as go
import colorlover as cl



def PeaksPlot(peaks, gage_id, notebook=True):
    peak_data = go.Scatter(x = peaks.index,
            y = peaks.values,
            mode='markers',
            marker=dict(
                size='8',
                color='blue',
                symbol = "circle-open" 
            )
        )

    data = [peak_data]

    layout = go.Layout(
        title='Peak Records at USGS {}'.format(gage_id),
        xaxis=dict(
            title='Year',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title='Discharge (cfs)',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )



    fig = go.Figure(data=data, layout=layout)
    if not notebook:
        interactive = plot(fig)
    else:
        interactive = iplot(fig)

def USGS_Plot(df, xlabel = None, ylabel = None, title = None, notebook=True):
    raw_data = df[df.columns[0]]
    
    gage_plot = go.Scatter(x = raw_data.index,
            y = raw_data.values,
            name='Flow',
            mode='line',
            marker=dict(
                size='16',
                color='blue'
            )
        )

    data = [gage_plot]

    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=xlabel,
            titlefont=dict(
                family='Courier New, monospace',
                size=16,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title=ylabel,
            titlefont=dict(
                family='Courier New, monospace',
                size=14,
                color='#7f7f7f'
            )
        )
    )
    
    
    fig = go.Figure(data=data, layout=layout)
    if not notebook:
        interactive = plot(fig)
    else:
        interactive = iplot(fig)

def NOAA_Plot(df_obs, df_preds, xlabel = None, ylabel = None, title = None, notebook=True):
    obs_data = df_obs[df_obs.columns[0]]
    pred_data = df_preds[df_preds.columns[0]]
    
    obs_plot = go.Scatter(x = obs_data.index,
            y = obs_data.values,
            name='Observed',
            mode='line',
            marker=dict(
                size='16',
                color='blue'
            )
        )
    
    pred_plot = go.Scatter(x = pred_data.index,
            y = pred_data.values,
            name='Prediccted',
            mode='line',
            marker=dict(
                size='16',
                color='#808080'
            )
        )

    data = [obs_plot, pred_plot]

    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=xlabel,
            titlefont=dict(
                family='Courier New, monospace',
                size=16,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title=ylabel,
            titlefont=dict(
                family='Courier New, monospace',
                size=14,
                color='#7f7f7f'
            )
        )
    )
    
    
    fig = go.Figure(data=data, layout=layout)
    if not notebook:
        interactive = plot(fig)
    else:
        interactive = iplot(fig)
        
        
def Double_axis_Plot(usgs, noaa, y_usgs_label = None,y_noaa_label = None,
                     x_label = None, title = None, notebook=True):
    
    raw_usgs = usgs[usgs.columns[0]]
    raw_noaa = noaa[noaa.columns[0]]
    
    usgs_plot = go.Scatter(x = raw_usgs.index,
            y = raw_usgs.values,
            name='USGS Flow',
            mode='line',
            marker=dict(
                size='16',
                color='blue'
            )
        )
    
    noaa_plot = go.Scatter(x = raw_noaa.index,
            y = raw_noaa.values,
            name='NOAA Stage',
            mode='line',
            yaxis='y2',
            marker=dict(
                size='16',
                color='#808080'
            )
        )

    data = [usgs_plot, noaa_plot]

    layout = go.Layout(
        title=title,
        xaxis=dict(
            title=x_label,
            titlefont=dict(
                family='Courier New, monospace',
                size=16,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            showgrid=False,
            title=y_usgs_label,
            range=[0, 500000],
            titlefont=dict(
                family='Courier New, monospace',
                size=14,
                color='#7f7f7f'
            )
        ),
        yaxis2=dict(
            title=y_noaa_label,
            range=[-2, 18],
            titlefont=dict(
                family='Courier New, monospace',
                size=14,
                color='#7f7f7f'
            ),
        overlaying='y',
        side='right'
        )
    )
    
    fig = go.Figure(data=data, layout=layout)
    if not notebook:
        interactive = plot(fig)
    else:
        interactive = iplot(fig)
        
        
def wind_rose_dev(df, data_col = 'wind_gust'):
    df.rename(columns = {'d':'wind_dir', 'g':'wind_gust', 's':'wind_speed'}, inplace=True)

    # Remove suspected erroneous data from wind speed
    wind_speed_error_detector = 100 # assume wind speed > 100 mph are erroneous (Hazel was highest of record, in DC: 98mph)
    wind_speed_errors = df.query('wind_speed > {}'.format(wind_speed_error_detector)).index
    wind_speed_errors
    df.drop(wind_speed_errors, axis = 0, inplace = True)

    # Remove suspected erroneous data from wind gusts
    wind_gust_error_detector = df['wind_speed'].max()*1.5 # assume wind gusts above 1.5*max speed are erroneous
    wind_gust_errors = df.query('wind_gust > {}'.format(wind_gust_error_detector)).index
    df.drop(wind_gust_errors, axis = 0, inplace = True)

    # Remove suspected erroneous data from wind dir
    wind_dir_error_detector = 360 # above 360 degrees is erroneous
    wind_dir_errors = df.query('wind_dir > {}'.format(wind_dir_error_detector)).index
    df.drop(wind_dir_errors, axis = 0, inplace = True)



    bin_range = range(0,int(np.ceil(df[data_col].max())+5),5)
    sort_range = range(0,int(np.ceil(df[data_col].max())+0),5)

    labels = [ "{0}-{1}".format(i, i + 5) for i in sort_range]
    df['group'] = pd.cut(df[data_col], bin_range, right=False, labels=labels)

    table = pd.pivot_table(df, values=data_col, index=['dr'],columns=['group'], aggfunc='count')
    del table.index.name

    dir_cat = ["N", "NNE", "NE", "ENE", "E","ESE", "SE" ,"SSE", 
               "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    dfnew = pd.DataFrame(dir_cat)
    dfnew.rename(columns={0:'r'}, inplace=True)
    dfnew.set_index('r', inplace=True)
    del dfnew.index.name
    dfnew.reset_index(inplace=True)
    dfnew.rename(columns={'index':'r'},inplace=True)

    for col in table:
        dfnew[col] = 0

    for i, idx in enumerate(dfnew['r']):
        heading_data = table[table.index==idx].values
        for data in heading_data:
            for j, d in enumerate(data):
                dfnew[dfnew.columns[j+1]].iloc[i] = d

    data = []
    counter = 0
    for col in dfnew.columns:
        if col != 'r':
            data.append(
                go.Area(t=dfnew['r'],
                        r=dfnew[col],
                        marker=dict(color=cl.scales['9']['seq']['PuBu'][counter]),
                        name=col+' knots' ) )
            counter+=1

    fig = go.Figure(data=data, layout=go.Layout(orientation=270, barmode='stack'))


    interactive = iplot(fig)
    