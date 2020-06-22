#!/usr/bin/python3

import os
import pandas as pd
import pytz
import yaml

from dt_help import Helper
from qstrader.asset.universe.static import StaticUniverse
from yahoofinancials import YahooFinancials

class DataProcessor():
    def __init__(self, input_directory, output_directory, input_prm_file):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.input_prm_file = input_prm_file
        self.data_dir = os.environ.get('QSTRADER_CSV_DATA_DIR')
        
    def __repr__(self):
        return(f'{self.__class__.__name__}({self.input_directory!r}, {self.output_directory!r}, {self.input_prm_file!r})')

    def __str__(self):
        return('input directory = {}, output directory = {}, input parameter file  = {}'.\
               format(self.input_directory, self.output_directory, self.input_prm_file))
        
    @Helper.timing
    def read_prm(self):
        filename = os.path.join(self.input_directory,self.input_prm_file)
        with open(filename) as fnm:
            self.conf = yaml.load(fnm, Loader=yaml.FullLoader)

    @Helper.timing
    def process(self):
        start_date = self.conf.get('start_date')
        end_date = self.conf.get('end_date')
        pairs = self.conf.get('pairs')
        
        date_range = Helper.get_spec_date(start_date, end_date)
        values = pd.DataFrame({'Date': date_range})
        values['Date']= pd.to_datetime(values['Date'])

        for i in pairs:
            raw_data = YahooFinancials(i)
            raw_data = raw_data.get_historical_price_data(start_date, end_date, "daily")
            df = pd.DataFrame(raw_data[i]['prices'])[['formatted_date','open','high','low','close','volume','adjclose']]
            df.columns = ['Date1'] + list(map(lambda x: x+i,['open_','high_','low_','close_','volume_','adjclose_']))
            df['Date1']= pd.to_datetime(df['Date1'])
            values = values.merge(df,how='left',left_on='Date',right_on='Date1')
            values = values.drop(labels='Date1',axis=1)

        values = values.fillna(method="ffill",axis=0)
        values = values.fillna(method="bfill",axis=0)
        cols = values.columns.drop('Date')
        values[cols] = values[cols].apply(pd.to_numeric,errors='coerce').round(decimals=3)
        values.set_index('Date',inplace=True)
        values_pairs0 = values[[el for el in values.columns if pairs[0] in el]]
        values_pairs1 = values[[el for el in values.columns if pairs[1] in el]]
        values_pairs0.columns = ['Open','High','Low','Close','Volume','Adj Close']
        values_pairs1.columns = ['Open','High','Low','Close','Volume','Adj Close']
        self.write_to(values_pairs0,pairs[0],self.data_dir,'csv')
        self.write_to(values_pairs1,pairs[1],self.data_dir,'csv')
        
    def view_data(self):
        print(self.data.head())
        
    def drop_cols(self,col_names): 
        self.data.drop(col_names, axis=1, inplace=True)
        return(self)
               
    def write_to(self,data,name,dir_out,flag):
        filename = os.path.join(dir_out,name)
        try:
            if('csv' in flag):
                data.to_csv(filename+'.'+flag)
            elif('xls' in flag):
                data.to_excel(filename+'.'+flag)
        except:
            raise ValueError("not supported format")
