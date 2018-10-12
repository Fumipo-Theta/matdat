import pandas as pd
from func_helper import identity, pip

from .plot_action import set_xlim, set_ylim, setStyle
from .csv_reader import CsvReader
from .get_path import PathList, getFileList
from .i_subplot import ISubplot
from .data_loader import DictLoader, DataFrameLoader, TableLoader, TestLoader


class Subplot(ISubplot):
    """
    Csvファイルを読み込み, その中のデータを変形し, プロットするメソッドを返す.
    Figureオブジェクトに登録することで最終的にプロットが作成される.

    Example
    -------
    fig=Figure(figureStyle):

    fig.add_subplot(
        Subplot.create(axStyle)\
            .register(
                data=getFileList(pattern1,pattern2,...)(directory),
                dataInfo={
                    "header": 3
                },
                plot=[scatterPlot(),linePlot()],
                option={
                    "xlim" : ["2018/08/10 00:00:00","2018/08/19 00:00:00"],
                    "y" : "Salinity",
                    "ylim" : [25,35],
                    "yLabel" : "Salinity"
                }
            )
    )
    """
    @staticmethod
    def create(style={}):
        subplot = Subplot(style)
        return subplot

    def __init__(self, style={}):
        self.dataReader = CsvReader()
        self.data = []
        self.dataInfo = []
        self.dataTransformer = []
        self.plotMethods = []
        self.option = []
        self.length = 0
        self.style = {
            "label_size": 16,
            "legend_size": 16,
            "tick_size": 14,
            "xTickRotation": 0,
            **style
        }

    @staticmethod
    def IDataReader(data_source):
        """
        Interface IDataReader

        read(data_source)
        transformBy(transformer_funcs)
        get(): pandas.DataFrame
        """

        if type(data_source) is dict:
            return DictLoader()

        elif type(data_source) is pd.DataFrame:
            return DataFrameLoader()
        else:
            return CsvReader()

    def plot(self, ax, test=False):
        """
        pyplot.axsubplot -> pyplot.axsubplot

        Apply plot action functions to ax.

        Parameters
        ----------
        ax: pyplot.axsubplot

        test: bool, optional
            Flag for test plot mode.
            Default value is False.

        Return
        ------
        plotted_ax: pyplot.axsubplot
            Ax applied the plot actions.
        """

        self.set_test_mode(test)

        actions = map(
            lambda i: self.__getPlotAction(i),
            range(self.length)
        )

        return pip(
            *actions
        )(ax)

    @staticmethod
    def __noDataAx(ax):
        ax.axis("off")
        return ax

    def setXaxisFormat(self):
        def f(ax):
            return ax
        return f

    def set_test_mode(self, test):
        self._isTest = test
        return self

    def isTest(self):
        return self._isTest

    def get_option(self, i):
        return self.option[i] if not self.isTest else {
            **self.option[i], "y": "y"}

    def __getPlotAction(self, i):
        df = self.read(i)
        opt = self.get_option(i)

        if len(df) == 0:
            return Subplot.__noDataAx

        return lambda ax: pip(
            set_xlim(df, opt),
            set_ylim(df, opt),
            *[f(df, opt) for f in self.plotMethods[i]],
            setStyle(opt, self.style),
            self.setXaxisFormat(),
        )(ax)

    def setIndex(self, i):
        return identity

    def filterX(self, i):
        if ("xlim" in self.option[i]):
            xlim = self.option[i]["xlim"]
            if ("x" in self.option[i]):
                x = self.option[i]["x"]
                return lambda df: df[(xlim[0] <= df[x]) & (df[x] <= xlim[1])]
            else:
                return lambda df: df[(xlim[0] <= df.index) & (df.index <= xlim[1])]
        else:
            return identity

    def read(self, i):
        if self.isTest():
            data_source = None
            loader = TestLoader()
            transformers = None

        elif type(self.data[i]) == dict:
            data_source = self.data[i]
            loader = DictLoader()
            transformers = self.dataTransformer[i]

        elif type(self.data[i]) == pd.DataFrame:
            data_source = self.data[i]
            loader = DataFrameLoader()
            transformers = self.dataTransformer[i]

        else:
            # path(s) of data source
            data_source = Subplot.__toPathList(self.data[i])
            loader = TableLoader()
            transformers = [
                self.setIndex(i),
                self.filterX(i),
                *self.dataTransformer[i]
            ]

        return loader.read(data_source, meta=self.dataInfo[i],
                           transformers=transformers)

    @staticmethod
    def __toPathList(pathLike):
        if type(pathLike) is PathList:
            return pathLike.files()
        elif type(pathLike) is list:
            return pathLike
        elif type(pathLike) is str:
            return [pathLike]
        else:
            raise TypeError("Invalid data source type.")

    def register(self, data,
                 dataInfo={}, plot=[],
                 option={},
                 **arg):
        transformer = arg.get("transformer") if arg.get(
            "transformer") != None else identity
        self.data.append(data)
        self.dataInfo.append({
            **dataInfo,
            **arg.get("header", {}),
            **arg.get("index", {})
        })
        self.plotMethods.append(plot)
        self.option.append({
            **option,
            **arg.get("limit", {}),
            **arg.get("xlim", {}),
            **arg.get("ylim", {})
        })
        self.dataTransformer.append(
            transformer if type(transformer) == list else [transformer])
        self.length = self.length+1
        return self

    def setPreset(self, preset):
        self.preset = preset
        return self

    def usePreset(self, name, fileSelector=[], plot=[], option={}, **arg):
        preset = self.preset[name]
        return self.register(
            data=getFileList(*fileSelector)(preset["directory"]),
            dataInfo=preset["dataInfo"],
            plot=[*preset["plot"], *
                  plot] if "plotOverwrite" not in arg else arg["plotOverwrite"],
            option={**preset["option"], **option},
            **arg
        )
