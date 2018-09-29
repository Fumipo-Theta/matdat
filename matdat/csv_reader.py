import pandas as pd
import chardet
from chardet.universaldetector import UniversalDetector
import re
from func_helper import pip, tee, mapping, filtering, reducing, identity
from IPython.display import display
from tqdm import tqdm


class CsvReader:
    """
    指定したパスのcsvファイルを読み込み, pandas.DataFrameへ変換する.

    Example
    -------
    from src.csv_reader import CsvReader

    reader = CsvReader()
    reader.setPath(path_to_csv, head=30, show=True)
    # The first 30 lines in {path_to_csv} file are shown.
    reader.read(header = 10)
    """

    def __init__(self, path=None, head=None, show=None):
        if path != None:
            self.setPath(path, head, show)

    @staticmethod
    def create(path=None, head=None, show=None):
        return CsvReader(path, head, show)

    def setPath(self, path: str, head: int=30, show: bool=False):
        self.path = path
        self.encoding = CsvReader.showLines(path, head, show)
        return self

    @staticmethod
    def showLines(path: str, head: int, show: bool):
        with open(path, mode='rb') as f:
            detector = UniversalDetector()
            i = 0
            lines = []
            for line in f:
                if (i >= head or detector.done):
                    break
                detector.feed(line)
                lines.append(line)
                i = i+1
            detector.close()
            encoding = detector.result['encoding'] if detector.result['encoding'] != None else "shift-JIS"
            # print(encoding+"?")
            if (show):
                pip(
                    enumerate,
                    mapping(lambda t: (t[0], str(t[1], encoding=encoding))),
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
                self.path, **arg)
        else:
            raise SystemError("Invalid file type.")
        return self

    @staticmethod
    def readCsv(path: str, **kwd):
        """
        Wrapper function for pandas.read_csv.
        """
        hasMultiByteChar = re.search(r"[^0-9a-zA-Z\._\-\s/\\]", path)

        engine = "python" if hasMultiByteChar else "c"

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

    @staticmethod
    def setTimeSeriesIndex(*columnName):
        """
        Set time series index to pandas.DataFrame
        datatime object is created from a column or two columns of
            date and time.
        The column "datetime" is temporally created,
            then it is set as index.

        Parameters
        ----------
        columnName: Union[str,List[str]]
            They can be multiple strings of column name or
                list of strings.

        Returns
        -------
        Callable[[pandas.DataFrame], pandas.DataFrame]

        """
        column = columnName[0] if type(columnName[0]) == list else columnName

        def f(df):
            df["datetime"] = pd.to_datetime(df[column[0]]) \
                if (len(column) == 1) \
                else pd.to_datetime(
                    df[column[0]] + " "+df[column[1]])

            df.set_index("datetime", inplace=True)
            return df
        return f

    def assembleDataFrame(self, *preprocesses):
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

        self.df = pd.concat(
            preprocessor(r) for r in tqdm(self.reader)
        )

        self.indexRange = [
            self.df.index.min(),
            self.df.index.max()
        ]
        return self

    def check(self, showFunc):
        self.showPath()
        return showFunc(self.df)

    def getDataFrame(self):
        return self.df
