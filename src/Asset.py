import pandas as pd
import numpy as np
from datetime import datetime
import time
import io

class Asset():
    def __init__(self, asset_name : str, source_type : str, **kwargs) -> None:
        self.asset_name = asset_name
        self.streaming = True
        self.datetime_format = kwargs["datetime_format"]
        self.datetime_column = kwargs["datetime_column"]
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")
        self.set_frequency(kwargs["frequency"])
        self.warmup = kwargs.get("warmup")
        if self.warmup != None: self.counter = 0

        if source_type == "csv":
            self.load_from_csv(
                csv_path = kwargs["csv_path"],
            )
        elif source_type == "zip":
            self.load_from_zip_file(
                f = kwargs["fp"]
            )

        self.trim_data()

    def reset(self):
        self.streaming = True
        self.counter = 0

    def set_frequency(self, frequency):
        if len(frequency) == 1: n = 1
        else: n = frequency[0]
        try: self.timedelta = np.timedelta64(n, frequency[-1])
        except: raise ValueError("invalid frequency passed to asset")

    def trim_data(self):
        if self.start_date == None: self.start_date = self.df.index[0]
        if self.end_date == None:   self.end_date = self.df.index[-1]
        self.df = self.df[(self.df.index >= self.start_date) & (self.df.index <= self.end_date)]
    def load_from_csv(self, csv_path : str):
        self.csv_path = csv_path
        dateparser = lambda x: datetime.strptime(x, self.datetime_format)

        self.df = pd.read_csv(
            filepath_or_buffer = self.csv_path,
            engine = 'c',
            parse_dates = [self.datetime_column],
            date_parser = dateparser,
            index_col = self.datetime_column
        )
        self.df.sort_index(inplace=True)
        self.datetime_last = self.df.index[-1]
        self.columns = self.df.columns

    def load_from_zip_file(self, f):
        dateparser = lambda x: datetime.strptime(x, self.datetime_format)
        file_string = io.StringIO(f.read().decode("utf-8"))

        self.df = pd.read_csv(
            file_string,
            parse_dates = [self.datetime_column],
            date_parser = dateparser,
            index_col = self.datetime_column
            )
        
        self.df.sort_index(inplace=True)
        self.datetime_last = self.df.index[-1]
        self.columns = self.df.columns

    def start_stream(self):
        self.counter += 1
        if self.counter <= self.warmup: return False
        return True

    def get_asset_view(self, current_market_time):
        if self.warmup != None:
            if not self.start_stream():
                return {}
        try:
            view = self.df.loc[current_market_time]
            if current_market_time == self.datetime_last: self.streaming = False
            return dict(zip(self.columns, view.values))
        except KeyError:
            return {}

if __name__ == "__main__":
    source_type = "csv"
    datetime_format = "%Y-%m-%d"
    datetime_column = "DATE"

    csv_path = r"C:\Users\bktor\Desktop\Python\FastTest\data\AAPL.csv"
    name = "AAPL"
    asset = Asset("AAPL",
        source_type = source_type,
        csv_path = csv_path,
        datetime_format = datetime_format,
        datetime_column = datetime_column
    )

    print(asset.df)