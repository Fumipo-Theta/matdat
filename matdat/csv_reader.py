import pandas as pd
import chardet
from chardet.universaldetector import UniversalDetector
import re
from func_helper import pip, tee, identity
import func_helper.func_helper.iterator as it
from IPython.display import display
from tqdm import tqdm

from .i_lazy_reader import ILazyReader

matchCsv = r"\.[cC](sv|SV)$"


class CsvReader(ILazyReader):
    """
    指定したパスのcsvファイルを読み込み, pandas.DataFrameへ変換する.

    Example
    -------
    from src.csv_reader import CsvReader

    reader = CsvReader()
    reader.setPath(path_to_csv, header=30, show=True)
    # The first 30 lines in {path_to_csv} file are shown.
    reader.read(header = 10)
    """

    def __init__(self, path: str=None, header: int=0, verbose: bool=False):
        self.is_verbose = verbose
        if path != None:
            self.setPath(path, header)

    @staticmethod
    def create(path: str=None, header: int=0, verbose: bool=False):
        return CsvReader(path, header, verbose)

    def setPath(self, path: str, header: int=30):
        self.path = path
        self.encoding = self.detect_encoding(path, header)
        return self

    def detect_encoding(self, path: str, header: int):
        with open(path, mode='rb') as f:
            detector = UniversalDetector()
            i = 0
            lines = []
            for line in f:
                if (i >= header or detector.done):
                    break
                detector.feed(line)
                lines.append(line)
                i = i+1
            detector.close()
            encoding = detector.result['encoding'] if detector.result['encoding'] != None else "shift-JIS"

            if self.is_verbose:
                pip(
                    enumerate,
                    it.mapping(lambda t: (t[0], str(t[1], encoding=encoding))),
                    list,
                    display
                )(lines)
            return encoding

    def read(self, header: int=0, **read_csv_kwd):
        """
        Indicate option in reading csv file with splitting.
        The reader of chunks, not pandas.DataFrame is generated.

        Parameters
        ----------
        header: int, optional
            Set header row number (start from 0 index).
            Default is 0.

        **read_csv_kwd:
            Key words capable to pandas.read_csv.
            As default, key words of "encoding" and "chunksize" are set.
            Default encoding is automatically estimated.
            Default chunksize is 100,000.

        Returns
        -------
        self
        """

        arg = {
            "header": header,
            "encoding": self.encoding,
            "chunksize": 100000,
            **read_csv_kwd
        }

        if (re.search(r"\.csv$", self.path, re.IGNORECASE) != None):
            self.reader = CsvReader.readCsv(
                self.path, self.is_verbose, **arg)
        else:
            raise SystemError("Invalid file type.")
        return self

    @staticmethod
    def readCsv(path: str, verbose: bool, **kwd):
        """
        Wrapper function for pandas.read_csv.
        """
        hasMultiByteChar = re.search(r"[^0-9a-zA-Z\._\-\s/\\]", path)

        engine = "python" if hasMultiByteChar else "c"
        engine = kwd.pop("engine", engine)
        if verbose:
            print("engine is:", engine)
            print("kwargs for pandas.read_csv:", kwd)

        try:
            return pd.read_csv(path, engine=engine, **kwd)
        except:
            return pd.read_csv(path, engine=engine,  **{**kwd, "encoding": "shift-JIS"})

    def getColumns(self):
        display(self.df.columns)
        return self.df.columns

    def showPath(self):
        print(self.path)

    def head(self, n: int = 1):
        self.showPath()
        return self.df.head(n)

    def assemble(self, *preprocesses):
        """
        Cocatenate all chunks preprocessed by some functions.
        DataFrame is created only after calling this method.

        Parameters
        ----------
        preprocesses: callable[[pandas.DataFrame], pandas.DataFrame]
            Functions for modifying pandas.DataFrame.
            Default is Identity function (no modification).
        """
        preprocessor = pip(
            *preprocesses) if len(preprocesses) > 0 else identity

        with tqdm(self.reader) as _tqdm:
            _tqdm.set_postfix(path=self.path)
            self.df = pd.concat(
                preprocessor(r) for r in _tqdm
            )

        self.indexRange = [
            self.df.index.min(),
            self.df.index.max()
        ]
        return self

    def assembleDataFrame(self, *preprocesses):
        print("Deplicated. Use assemble()")
        return self.assemble(*preprocesses)

    def check(self, showFunc):
        self.showPath()
        return showFunc(self.df)

    def getDataFrame(self):
        return self.df
