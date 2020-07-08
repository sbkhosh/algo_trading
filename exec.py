#!/usr/bin/python3

import matplotlib
import os
import pandas as pd 
import warnings

from dt_help import Helper
from dt_read import DataProcessor
from dt_model import Strategy
from pandas.plotting import register_matplotlib_converters

warnings.filterwarnings('ignore',category=FutureWarning)
pd.options.mode.chained_assignment = None 
register_matplotlib_converters()

if __name__ == '__main__':
    obj_helper = Helper('data_in','conf_help.yml')
    obj_helper.read_prm()
    
    fontsize = obj_helper.conf['font_size']
    matplotlib.rcParams['axes.labelsize'] = fontsize
    matplotlib.rcParams['xtick.labelsize'] = fontsize
    matplotlib.rcParams['ytick.labelsize'] = fontsize
    matplotlib.rcParams['legend.fontsize'] = fontsize
    matplotlib.rcParams['axes.titlesize'] = fontsize
    matplotlib.rcParams['text.color'] = 'k'

    obj_reader = DataProcessor('data_in','data_out','conf_model.yml')
    obj_reader.read_prm()
    obj_reader.process()

    strat = Strategy(obj_reader.conf.get('pairs'),
                     start_dt=obj_reader.conf.get('start_date'),
                     end_dt=obj_reader.conf.get('end_date'))

    strat.get_strategy()
    strat.get_benchmark_asset()
    strat.get_tearsheet()
