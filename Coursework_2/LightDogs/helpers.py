import pandas as pd


def load_data_light(filepath):
    # Function to load in the light data from CSVs

    light_df = pd.DataFrame()

    new_light = pd.read_csv(filepath, header=None, parse_dates=[0])
    light_df = light_df.append(new_light)

    # Name Columns
    light_df.columns = ['datetime', 'light_level']

    # Convert to datetime
    light_df['datetime'] = pd.to_datetime(light_df['datetime'], format='%Y-%m-%d %H:%M:%S.%f')

    # Sort chronologically
    Light = light_df.sort_values(by='datetime')
    Light.set_index(['datetime'], inplace=True)

    return Light


def load_data_twitter(filepath):
    # Function to load in the twitter data from CSVs

    twitter_df = pd.DataFrame()

    # Import Twitter Data
    new_twitter = pd.read_csv(filepath, header=None, parse_dates=[1], usecols=[1, 2, 3])
    twitter_df = twitter_df.append(new_twitter)

    # Name Columns
    twitter_df.columns = ['datetime', 'sentiment', 'text']

    # Convert to datetime
    twitter_df['datetime'] = pd.to_datetime(twitter_df['datetime'], format='%Y-%m-%d %H:%M:%S.%f')

    # Sort chronologically
    Twitter = twitter_df.sort_values(by='datetime')
    Twitter.set_index(['datetime'], inplace=True)

    return Twitter
