import pandas as pd
from .data_loader import DictLoader, DataFrameLoader, TableLoader, TestLoader


class ISubplot:

    def plot(self, ax, test=False):
        return ax

    def set_test_mode(self, test):
        self._isTest = test
        return self

    def isTest(self):
        return self._isTest

    @staticmethod
    def IDataLoader(data_source, isTest):
        if isTest:
            return TestLoader()

        elif type(data_source) == dict:
            return DictLoader()

        elif type(data_source) == pd.DataFrame:
            return DataFrameLoader()

        else:
            # path like values of data source
            return TableLoader()
