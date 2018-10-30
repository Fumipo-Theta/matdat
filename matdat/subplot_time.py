import pandas as pd
import matplotlib.dates as mdates
from .subplot import Subplot
from .csv_reader import CsvReader


class SubplotTime(Subplot):
    """
    時系列のためのsubplotを生成する.

    Example
    -------
    fig=Figure(figureStyle):

    fig.add_subplot(
        SubplotTime.create(axStyle)\
            .register(
                data=getFileList(pattern1,pattern2,...)(directory),
                dataInfo={
                    "header": 3,
                    "index" : ["datetime"]
                },
                plot=[scatterPlot(),linePlot()],
                option={
                    "y" : "Salinity",
                    "ylim" : [25,35],
                    "yLabel" : "Salinity"
                },
                limit={
                    "xlim" : ["2018/08/10 00:00:00","2018/08/19 00:00:00"]
                }
            )
    )
    """

    @staticmethod
    def create(style={}):
        subplot = SubplotTime(style)
        return subplot

    def __init__(self, style={}):
        super().__init__({"xFmt": "%m/%d", **style})

    def plot(self, ax, test=False):
        if ("xlim" in self.global_limit):
            self.global_limit["xlim"] = pd.to_datetime(
                self.global_limit["xlim"])
        return super().plot(ax, test)

    def setXaxisFormat(self):
        def f(ax):
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter(
                    self.style["xFmt"]
                )
            )
            return ax
        return f

    def setIndex(self, i):
        return CsvReader.setTimeSeriesIndex(
            *self.index_name[i]
        )

    def read(self, i):

        if self.isTest():
            data_source = pd.DataFrame({
                "x": pd.to_datetime([
                    "1990/10/07 00:00:00",
                    "2010/10/07 00:00:00",
                    "2030/10/07 00:00:00"
                ]),
                "y": [0, 20, 40]
            })
            return data_source.set_index("x")

        return super().read(i)
