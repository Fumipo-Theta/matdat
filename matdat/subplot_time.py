import pandas as pd
import matplotlib.dates as mdates
from .subplot import Subplot
from .csv_reader import CsvReader
from func_helper import identity
import func_helper.func_helper.dataframe as dataframe
from . import plot
from func_helper.func_helper.iterator import DuplicateLast as Duplicated


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
    def create(*style_dict, **style):
        subplot = SubplotTime(*style_dict, **style)
        return subplot

    def __new__(cls, *arg, **kwargs):
        return super().__new__(cls)

    def __init__(self, *style_dict, **style):
        super().__init__(*style_dict, **{
            # "xFmt": "%m/%d",
            **style
        })
        self.filter_x = True

    def plot(self, ax, test=False):
        if ("xlim" in self.axes_style and type(self.axes_style["xlim"]) is not pd.core.indexes.datetimes.DatetimeIndex):
            self.axes_style["xlim"] = pd.to_datetime(
                self.axes_style["xlim"])
        return super().plot(ax, test)

    def setXaxisFormat(self):
        def f(ax):
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter(
                    self.axes_style["style"].get("xFmt", None)
                )
            )
            return ax
        return f

    def default_transformers(self, i) -> tuple:

        def filterX():
            x = self.option[i].get("x", None)
            lim = self.axes_style.get("xlim", [])
            if len(lim) == 0 or lim is None:
                return identity
            elif len(lim) == 1:
                lower = lim[0]
                upper = None
            else:
                lower, upper, *_ = lim

            return lambda df: dataframe.filter_between(
                *(pd.to_datetime([lower, upper]) if type(lower)
                  is not pd.core.indexes.datetimes.DatetimeIndex else [lower, upper]), False, False
            )(df, x) if self.filter_x else df

        def setIndex(index_name):

            if type(index_name) is str:
                return dataframe.setTimeSeriesIndex(
                    index_name
                )
            if type(index_name) is not list:
                return identity
            elif len(index_name) == 0:
                return identity
            else:
                return dataframe.setTimeSeriesIndex(
                    *index_name
                )

        index_names = self.index_name[i].args if type(
            self.index_name[i]) is Duplicated else(self.index_name[i],)

        return Duplicated(*[[setIndex(index_name), filterX()] for index_name in index_names])

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

    def register(self, *arg, within_xlim=True, **kwargs):
        return super().add(*arg, within_xlim=within_xlim, **kwargs)

    def add(self, *arg, within_xlim=True, **kwargs):
        return super().add(*arg, within_xlim=within_xlim, **kwargs)
