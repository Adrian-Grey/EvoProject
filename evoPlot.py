import pandas as pd
import numpy as np
import plotly.express as px

pd.options.plotting.backend = "plotly"

color_frame = pd.read_csv('population.csv', usecols = ['time', 'average_red', 'average_green', 'average_blue'])

color_frame.plot(x='time', y=['average_blue','average_red','average_green']).show()
