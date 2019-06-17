from flask import Flask
from helpers import load_data_light, load_data_twitter
from os.path import dirname, join, abspath

# Import the data
Light = load_data_light(join(dirname(__file__), 'data', 'l_out.csv'))
Twitter = load_data_twitter(join(dirname(__file__), 'data', 't_out.csv'))

app = Flask(__name__)  # create the app
app._static_folder=join(dirname(__file__), 'static')  # make the static folder discoverable
app.secret_key = 'SHH!'

from LightDogs import routes