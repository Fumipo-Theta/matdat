import pandas as pd
import re
from typing import Callable, List
from func_helper import pip, identity
from .i_lazy_reader import ILazyReader

DataFrame_transformer = Callable[[pd.DataFrame], pd.DataFrame]

matchExcel = r"^(?!.*\~\$).*\.xlsx?$"


class ExcelReader(ILazyReader):
    def __init__(self, path: str=None, header: int=0, verbose: bool=False):
        self.is_verbose = verbose
        if path:
            self.setPath(path, header)

    @staticmethod
    def create(*arg, **kwargs):
        return ExcelReader(*arg, **kwargs)

    def setPath(self, path: str, header: int=30):
        self.path = path
        return self

    def read(self, header: int=0, **read_excel_kwargs):

        arg = {
            "header": header,
            **read_excel_kwargs
        }
        if (re.search(r"\.xlsx?$", self.path, re.IGNORECASE) != None):
            self.reader = ExcelReader.readExcel(
                self.path, self.is_verbose, **arg)
        else:
            raise SystemError("Invalid file type.")
        return self

    @staticmethod
    def readExcel(path, verbose, **kwargs):
        if verbose:
            print(f"kwargs for pandas.read_excel: {kwargs}")

        return pd.read_excel(path, **kwargs)

    def assemble(self, *preprocesses: DataFrame_transformer):
        preprocessor = pip(
            *preprocesses
        ) if preprocesses else identity

        self.df = preprocessor(self.reader)

        return self

    def getDataFrame(self):
        return self.df
