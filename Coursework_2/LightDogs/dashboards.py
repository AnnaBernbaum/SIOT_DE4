from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column
import statsmodels.api as sm
import numpy as np

class Dashboards:

    def dashboard_timeline(self, data_light, data_twitter_binned, Sentiment):
        # Function to create plots for the timeline page

        # source_light = {'datetime':data_light.index, 'light_level':data_light['light_level']}
        data_light['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_light.index]
        data_twitter_binned['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_twitter_binned.index]
        Sentiment['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in Sentiment.index]

        source_light = ColumnDataSource(data_light)
        source_twitter = ColumnDataSource(data_twitter_binned)

        # Create Light-Time plot
        plot_light = self.create_plot_light(source_light, 'Light Level', 'DateTime', 'Light Level (lx)')

        # Create Twitter-Time Plot
        plot_twitter = self.create_plot_twitter(source_twitter, 'Tweet Incidence', 'DateTime',
                                                'Tweet Incidence per Hour (no. of tweets)', plot_light)

        # Create Sentiment-Time Plot
        plot_sentiment = self.create_plot_sentiment(Sentiment, 'Sentiment Score', plot_light)

        # create grid of plots
        layout = column([plot_light, plot_twitter, plot_sentiment])
        script, div = components(layout)

        return script, div

    def dashboard_analysis(self, data_light_binned, data_twitter_binned, Sentiment):
        # Function to create plots for the analysis page

        # ACF plot Light
        allTimeLags, autoCorr ,selectedLagPoints, selectedAutoCorr= self.acf(data_light_binned)
        source_light_acf = ColumnDataSource({'x1': allTimeLags, 'y1': autoCorr})
        source_light_acf_selected = ColumnDataSource({'x2':selectedLagPoints, 'y2':selectedAutoCorr})
        acf_plot_light = self.create_acf_plot(source_light_acf, source_light_acf_selected, 'Light Level ACF', plot=None)

        # ACF Plot Twitter
        allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr = self.acf(data_twitter_binned)
        source_twitter_acf = ColumnDataSource({'x1': allTimeLags, 'y1': autoCorr})
        source_twitter_acf_selected = ColumnDataSource({'x2': selectedLagPoints, 'y2': selectedAutoCorr})
        acf_plot_twitter = self.create_acf_plot(source_twitter_acf, source_twitter_acf_selected, 'Tweet Incidence ACF', plot=None)

        # ACF Plot Sentiment
        allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr = self.acf(Sentiment)
        source_sentiment_acf = ColumnDataSource({'x1': allTimeLags, 'y1': autoCorr})
        source_sentiment_acf_selected = ColumnDataSource({'x2': selectedLagPoints, 'y2': selectedAutoCorr})
        acf_plot_sentiment = self.create_acf_plot(source_sentiment_acf, source_sentiment_acf_selected, 'Tweet Sentiment ACF', plot=None)

        # Both datasets together and normalised
        norm_light = (data_light_binned['light_level'] - np.mean(data_light_binned['light_level'])) / np.std(
            data_light_binned['light_level'])
        norm_twitter = (data_twitter_binned['count'] - np.mean(data_twitter_binned['count'])) / np.std(data_twitter_binned['count'])
        norm_sentiment = (Sentiment['Score']-np.mean(Sentiment['Score'])) / np.std(Sentiment['Score'])

        # load into normalised dataframes
        norm_light_cds = ColumnDataSource({'datetime': data_light_binned.index, 'light_level': norm_light})
        norm_twitter_cds = ColumnDataSource({'datetime': data_twitter_binned.index, 'count': norm_twitter})
        norm_sentiment_cds = ColumnDataSource({'datetime':Sentiment.index, 'score':norm_sentiment})

        # Normalised Plot
        norm = self.create_norm_plot(norm_light_cds, norm_twitter_cds, norm_sentiment_cds, 'Normalised Datasets')

        # Labels for tooltiops
        data_twitter_binned['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_twitter_binned.index]
        Sentiment['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in Sentiment.index]

        # Trends seasonality and noise
        light_decomposed = sm.tsa.seasonal_decompose(norm_light, freq=24)  # The frequency is daily
        tooltip = [x.strftime("%Y-%m-%d %H:%M:%S") for x in light_decomposed.trend.index]
        l_trend = ColumnDataSource({'datetime':light_decomposed.trend.index, 'y': light_decomposed.trend, 'tooltip':tooltip})
        l_seasonal = ColumnDataSource({'datetime':light_decomposed.seasonal.index, 'y': light_decomposed.seasonal, 'tooltip':tooltip})
        l_noise = ColumnDataSource({'datetime':light_decomposed.resid.index, 'y': light_decomposed.resid, 'tooltip':tooltip})

        twitter_decomposed = sm.tsa.seasonal_decompose(norm_twitter, freq=24)  # The frequency is daily
        t_trend = ColumnDataSource({'datetime':twitter_decomposed.trend.index, 'y': twitter_decomposed.trend, 'tooltip':tooltip})
        t_seasonal = ColumnDataSource({'datetime':twitter_decomposed.seasonal.index, 'y': twitter_decomposed.seasonal, 'tooltip':tooltip})
        t_noise = ColumnDataSource({'datetime':twitter_decomposed.resid.index, 'y': twitter_decomposed.resid, 'tooltip':tooltip})

        sentiment_decomposed = sm.tsa.seasonal_decompose(norm_sentiment, freq=24)  # The frequency is daily
        s_trend = ColumnDataSource({'datetime':sentiment_decomposed.trend.index, 'y': sentiment_decomposed.trend, 'tooltip':tooltip})
        s_seasonal = ColumnDataSource({'datetime':sentiment_decomposed.seasonal.index, 'y': sentiment_decomposed.seasonal, 'tooltip':tooltip})
        s_noise = ColumnDataSource({'datetime':sentiment_decomposed.resid.index, 'y': sentiment_decomposed.resid, 'tooltip':tooltip})

        trend = self.create_seasonality_plot(l_trend, t_trend, s_trend, 'Trend', None)
        seasonality = self.create_seasonality_plot(l_seasonal, t_seasonal, s_seasonal, 'Seasonality', None)
        noise = self.create_seasonality_plot(l_noise, t_noise, s_noise, 'Noise', None)

        # Correlation of datasets
        corr_light_twitter = norm_light.corr(norm_twitter)
        corr_light_senti = norm_light.corr(norm_sentiment)
        correlation = [corr_light_twitter, corr_light_senti]

        # Create layouts
        trends = column([trend, seasonality, noise])
        layout = column([acf_plot_light, acf_plot_twitter, acf_plot_sentiment])

        # Scripts and divs to return
        script1, div1 = components(norm)
        script2, div2 = components(layout)
        script3, div3 = components(trends)

        return script1, div1, script2, div2, script3, div3, correlation

    def create_plot_light(self, source, title, x_name, y_name,hover_tool=None,
                         width=1100, height=300):
        # Function to create light plots for the timeline page

        plot = figure(title=title,plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label=x_name, y_axis_label=y_name)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('Light Level (lx)', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='light_level', line_width=2, source=source)

        return plot

    def create_plot_twitter(self, source, title, x_name, y_name, plot,
                         width=1100, height=300):
        # Function to create twitter plots for the timeline page

        plot = figure(title=title,plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label=x_name, y_axis_label=y_name, x_range=plot.x_range)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('Tweets per Hour', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='count', line_width=2, source=source)

        return plot

    def create_plot_sentiment(self, source, title, plot,
                         width=1100, height=300):
        # Function to create sentiment plots for the timeline page

        plot = figure(title=title, plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label='Datetime', y_axis_label='Tweet Sentiment Score', x_range=plot.x_range)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('Sentiment Score', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='Score', line_width=2, source=source)

        return plot

    def create_acf_plot(self, source, select_source, title, plot,
                         width=1100, height=300):
        # Function to create acf plots for the analysis page

        plot = figure(title=title,plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['save'],
                      outline_line_color="#666666",
                      x_axis_label='Time Lag (Hours)', y_axis_label='Correlation Coefficient')

        plot.line(x='x1', y='y1', line_width=2, source=source)


        plot.add_tools(HoverTool(
            tooltips=[
                ('Timelag', '@x1{f} hours'),
                ('Correlation Coefficient', '@y1{0.2f}'),
            ],

            # display a tooltip whenever the cursor is vertically in line with a glyph
            mode='vline'))

        plot.circle(x='x2', y='y2', source=select_source, size=5)

        return plot

    def create_norm_plot(self, source_light, source_twitter, source_sentiment, title,
                         width=1100, height=300):
        # Function to create normalised plots for the analysis page

        plot = figure(title=title,plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label='Date')

        plot.line(x='datetime', y='light_level', line_width=2, source=source_light, legend='Light Level')
        plot.line(x='datetime', y='count', line_width=2, line_color="red", source=source_twitter, legend='Twitter Count')
        plot.line(x='datetime', y='score', line_width=2, line_color="green", source=source_sentiment, legend='Tweet Sentiment Score')

        plot.legend.click_policy = "hide"  # interactive legend

        return plot

    def create_seasonality_plot(self, source1, source2, source3, title, xlabel,
                         width=1100, height=300):
        # Function to create seasonality plots for the analysis page

        plot = figure(title=title, plot_width=width,
                      plot_height=height, h_symmetry=False, v_symmetry=False,
                      min_border=0, toolbar_location="above", tools=['save', 'pan', 'wheel_zoom', 'reset'],
                      outline_line_color="#666666", x_axis_type = 'datetime',
                      x_axis_label=xlabel)

        plot.line(x='datetime', y='y', line_width=2, source=source1, legend='Light Levels')
        plot.line(x='datetime', y='y', line_width=2, source=source2, line_color='red', legend='Twitter Count')
        plot.line(x='datetime', y='y', line_width=2, source=source3, line_color='green', legend='Tweet Sentiment')

        plot.legend.click_policy = "hide"

        return plot

    def acf(self, data):
        # Function to calculate acf for the analysis page

        # Change to a one column data series
        data_series = data.ix[:,0]

        selectedLagPoints = [24, 48, 72]  # points to highlight
        maxLagDays = 7
        allTimeLags = np.arange(1, maxLagDays * 24)

        autoCorr = [data_series.autocorr(lag=dt) for dt in allTimeLags]
        selectedAutoCorr = [data_series.autocorr(lag=dt) for dt in selectedLagPoints]

        return allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr