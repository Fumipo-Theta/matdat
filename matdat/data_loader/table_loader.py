from .i_data_loader import IDataLoader
from ..csv_reader import CsvReader
import pandas as pd


class TableLoader(IDataLoader):
    def __init__(self):
        pass

    def read(self, paths, meta={}, transformers=[]):
        reader = CsvReader()
        dfs = []
        for path in paths:
            reader.setPath(path)
            reader.read(meta)
            reader.assembleDataFrame(*transformers)
            dfs.append(reader.df)

        return pd.concat(dfs) if len(dfs) > 0 else []
