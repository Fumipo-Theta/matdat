from .i_data_loader import IDataLoader
from ..csv_reader import CsvReader
from ..excel_reader import ExcelReader
from ..get_path import PathList
import pandas as pd
import re

ext = {
    "csv": r'\.[cC](sv|SV)$',
    "excel": r"^(?!.*\~\$).*\.xlsx?$"
}


class TableLoader(IDataLoader):
    def __init__(self):
        pass

    def read(self, path_like, meta={}, transformers=[]):
        paths = TableLoader.toPathList(path_like)

        dfs = []
        for path in paths:
            reader = TableLoader.IReader(path)
            reader.setPath(path)
            reader.read(**meta)
            reader.assemble(*transformers)
            dfs.append(reader.df)

        return pd.concat(dfs, sort=True) if len(dfs) > 0 else []

    @staticmethod
    def IReader(path):
        if (re.search(r"\.csv$", path, re.IGNORECASE) != None):
            return CsvReader()

        elif (re.search(r"\.xlsx?$", path, re.IGNORECASE) != None):
            return ExcelReader()

        else:
            raise SystemError(f"Invalid file type: {path}")

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
