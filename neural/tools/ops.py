from datetime import datetime
from typing import List, Iterable, Dict
from enum import Enum

import pandas_market_calendars as market_calendars
import pandas as pd
import tableprint, re, os
from tqdm import tqdm

from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from neural.tools.enums import CalendarType
from neural.core.data.enums import DatasetType, ColumnType


class Calendar:

    def __init__(
        self, 
        calendar_type=CalendarType
        ) -> None:
        
        self.calendar_type = calendar_type
        self.calendar = None

    def get_calendar(self):

        calendar = market_calendars.get_calendar(self.calendar_type.value)

        return calendar

    # get core hours of calendar
    def get_schedule(
            self, 
            start_date, 
            end_date
            ) -> pd.DataFrame:

        self.calendar = self.get_calendar()
        
        # Time returned is always UTC
        schedule = self.calendar.schedule(
            start_date=start_date, end_date=end_date)

        return schedule

    def get_time_zone(self) -> str:

        if self.calendar_type == CalendarType.ALWAYS_OPEN:
            time_zone = 'UTC'

        elif self.calendar_type == CalendarType.NYSE:
            time_zone = 'America/New_York'

        return time_zone
    

def validate_path(
    file_path: str | os.PathLike
    ) -> None:

    if os.path.isdir(file_path):
        raise ValueError(
            "The specified path is a directory, not a file.")
    
    else:
        dir_path = os.path.dirname(file_path)

        if not os.path.isdir(dir_path):
            raise ValueError(
                "The directory leading to the specified file does not exist.")
        
    return None

def create_column_schema(data: pd.DataFrame):

    column_schema = dict()

    for column_type in ColumnType:

        mask = data.columns.str.match(column_type.value.lower())
        column_schema[column_type] = mask

    return column_schema

def to_datetime(date: str):

    try:
        date_format = "%d/%m/%Y"
        date_time_ = datetime.strptime(date, date_format)

    except:
        raise ValueError('Invalid date. Valid examples: 20/03/2018, 01/01/2015')

    return date_time_


def to_timeframe(time_frame: str):

    match = re.search(r'(\d+)(\w+)', time_frame)

    if match:

        amount = int(match.group(1))
        unit = match.group(2)

        map = {
            'Min': TimeFrameUnit.Minute,
            'Hour': TimeFrameUnit.Hour,
            'Day': TimeFrameUnit.Day,
            'Week': TimeFrameUnit.Week,
            'Month': TimeFrameUnit.Month}

        return TimeFrame(amount, map[unit])
    
    else:
        raise ValueError(
            "Invalid timeframe. Valid examples: 59Min, 23Hour, 1Day, 1Week, 12Month")

def tabular_print(
        entries: List, style='banner',
        align='left', width = 15, header = False) -> None:
    
    # helper method to tabulate performance metrics.
    if header:
        row = tableprint.header(
            entries, style=style, align=align, width=width)

    else:
        row = tableprint.row(
            entries, style=style, align=align, width=width)

    return row

def progress_bar(total: Iterable):
    bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt} | {elapsed}<{remaining}'
    bar = tqdm(total = total, bar_format = bar_format)
    return bar


def sharpe(assets_hist: List[float], base=0):

    hist = pd.Series(assets_hist)
    returns = hist.pct_change().dropna()
    val = (returns.mean()-base)/returns.std()

    return val

# converts collection of enum objects dataframe.
def objects_to_df(
    object_collection: Iterable[Dict[str, str]]
    ) -> pd.DataFrame:
    
    objects_collection_ = object_collection.copy()
    for index, object in enumerate(objects_collection_):
        object_dict = dict(object)

        for key, val in object_dict.items():
            object_dict[key] = val.value if isinstance(val, Enum) else val
            objects_collection_[index] = object_dict

    df = pd.DataFrame(objects_collection_)
    return df
