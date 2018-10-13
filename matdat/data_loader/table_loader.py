from .i_data_loader import IDataLoader
from ..csv_reader import CsvReader
from ..get_path import PathList
import pandas as pd


class TableLoader(IDataLoader):
    def __init__(self):
        pass

    def read(self, path_like, meta={}, transformers=[]):
        paths = TableLoader.toPathList(path_like)

        reader = CsvReader()
        dfs = []
        for path in paths:
            reader.setPath(path)
            reader.read(**meta)
            reader.assembleDataFrame(*transformers)
            dfs.append(reader.df)

        return pd.concat(dfs) if len(dfs) > 0 else []

    @staticmethod
    def toPathList(pathLike):
        if type(pathLike) is PathList:
            return pathLike.files()
        elif type(pathLike) in [list, tuple]:
            return pathLike
        elif type(pathLike) is str:
            return [pathLike]
        else:
            raise TypeError("Invalid data source type.")
