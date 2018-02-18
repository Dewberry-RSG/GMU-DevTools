from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#print(__version__) # requires version >= 1.9.0
init_notebook_mode(connected=True)
import plotly.plotly as py
import plotly.graph_objs as go


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

def Simple_Plot(df, xlabel = None, ylabel = None, title = None, notebook=True):
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