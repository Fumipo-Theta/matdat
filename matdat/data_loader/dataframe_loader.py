from .i_data_loader import IDataLoader
from func_helper import pip, identity
import pandas as pd


class DataFrameLoader(IDataLoader):
    def __init__(self):
        pass

    def read(self, data, meta={}, transformers=[identity]):
        return pip(*transformers)(
            data)
