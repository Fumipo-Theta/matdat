import pandas as pd
import matplotlib.dates as mdates
from .subplot import Subplot
from .csv_reader import CsvReader
from func_helper import identity
import func_helper.func_helper.dataframe as dataframe


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
                y="Salinity",
                ylim= [25,35],
                ylabel= "Salinity",
                xlim= ["2018/08/10 00:00:00","2018/08/19 00:00:00"]

            )
    )
    """

    @staticmethod
    def create(style={}):
        subplot = SubplotTime(style)
        return subplot

    def __init__(self, style={}):
        super().__init__({
            "xFmt": "%m/%d",
            **style
        })

    def plot(self, ax, test=False):
        if ("xlim" in self.axes_style and type(self.axes_style["xlim"]) is not pd.core.indexes.datetimes.DatetimeIndex):
            self.axes_style["xlim"] = pd.to_datetime(
                self.axes_style["xlim"])
        return super().plot(ax, test)

    def setXaxisFormat(self):
        def f(ax):
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter(
                    self.axes_style["style"]["xFmt"]
                )
            )
            return ax
        return f

    def default_transformers(self, i):

        def filterX():
            x = self.option[i].get("x", None)
            lim = self.axes_style.get("xlim", [])
            if len(lim) is 0:
                lim = lim+[None, None]
            elif len(lim) is 1:
                lim = lim + [None]

            return lambda df: dataframe.filter_between(
                *(pd.to_datetime(lim) if type(lim) is not pd.core.indexes.datetimes.DatetimeIndex else lim)
            )(df, x)

        def setIndex():
            if type(self.index_name[i]) is not list:
                return dataframe.setTimeSeriesIndex(
                    self.index_name[i]
                )

            if len(self.index_name[i]) is 0:
                return identity
            else:
                return dataframe.setTimeSeriesIndex(
                    *self.index_name[i]
                )

        return [setIndex(), filterX()]

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
