import pandas as pd
import numpy as np
from datetime import datetime
import time

class Asset():
    def __init__(self, asset_name : str, source_type : str, **kwargs) -> None:
        self.asset_name = asset_name
        self.streaming = True
        self.set_frequency(kwargs["frequency"])
        if source_type == "csv":
            self.load_from_csv(
                csv_path = kwargs["csv_path"],
                datetime_format = kwargs["datetime_format"],
                datetime_column = kwargs["datetime_column"]
            )

    def set_frequency(self, frequency):
        if len(frequency) == 1: n = 1
        else:                   n = frequency[0]
        try: self.timedelta = np.timedelta64(n, frequency[-1])
        except: raise ValueError("invalid frequency passed to asset")
        

    def load_from_csv(self, csv_path : str, datetime_format : str, datetime_column : str):
        self.csv_path = csv_path
        self.datetime_format = datetime_format
        self.datetime_column = datetime_column
        dateparser = lambda x: datetime.strptime(x, self.datetime_format)

        self.df = pd.read_csv(
            filepath_or_buffer = self.csv_path,
            engine = 'c',
            parse_dates = [self.datetime_column],
            date_parser = dateparser,
            index_col = self.datetime_column
        )
        self.df.sort_index(inplace=True)
        self.columns = self.df.columns

    def get_asset_view(self, current_market_time):
        try:
            view = self.df.loc[current_market_time]
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