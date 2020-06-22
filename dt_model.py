#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from dt_help import Helper
from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.asset.equity import Equity
from qstrader.asset.universe.static import StaticUniverse
from qstrader.data.backtest_data_handler import BacktestDataHandler
from qstrader.data.daily_bar_csv import CSVDailyBarDataSource
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading.backtest import BacktestTradingSession

class Strategy():
    def __init__(
        self,
        pairs,
        start_dt,
        end_dt
    ):
        self.pairs = pairs
        self.assets = ['EQ:%s' % symbol for symbol in self.pairs]
        self.strategy_universe = StaticUniverse(self.assets)
        self.start_dt = pd.to_datetime(start_dt).tz_localize('UTC')
        self.end_dt = pd.to_datetime(end_dt).tz_localize('UTC')
        
    def get_strategy(self):
        csv_dir = os.environ.get('QSTRADER_CSV_DATA_DIR','.')
        self.data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=self.pairs)
        self.data_handler = BacktestDataHandler(self.strategy_universe, data_sources=[self.data_source])
        self.cash_buffer_percentage = 0.01
        
        self.strategy_alpha_model = FixedSignalsAlphaModel({self.assets[0]: 0.6, self.assets[1]:0.4})
        strategy_backtest = BacktestTradingSession(
            self.start_dt,
            self.end_dt,
            self.strategy_universe,
            self.strategy_alpha_model,
            rebalance='end_of_month',
            cash_buffer_percentage=self.cash_buffer_percentage,
            data_handler=self.data_handler)
        self.strategy_backtest = strategy_backtest
        self.strategy_backtest.run()

    def get_benchmark_asset(self):
        self.benchmark_universe = StaticUniverse([self.assets[0]])
        self.benchmark_alpha_model = FixedSignalsAlphaModel({self.assets[0]: 1.0})
        benchmark_backtest = BacktestTradingSession(
            self.start_dt,
            self.end_dt,
            self.benchmark_universe,
            self.benchmark_alpha_model,
            rebalance='weekly',
            rebalance_weekday='THU',
            cash_buffer_percentage=self.cash_buffer_percentage,
            data_handler=self.data_handler
        )
        self.benchmark_backtest = benchmark_backtest
        self.benchmark_backtest.run()
        
    def get_tearsheet(self):
        tearsheet = TearsheetStatistics(
            strategy_equity=self.strategy_backtest.get_equity_curve(),
            benchmark_equity=self.benchmark_backtest.get_equity_curve(),
            title='60/40 US Equities/Bonds'
        )
        tearsheet.plot_results()
        plt.show()
