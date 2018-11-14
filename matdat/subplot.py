import pandas as pd
from func_helper import identity, pip

from .plot_action import set_xlim, set_ylim, setStyle
import matdat.matdat.plot as plot
from .get_path import PathList, getFileList
from .i_subplot import ISubplot


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
    def create(style={}, title=None):
        subplot = Subplot(style, title)
        return subplot

    def __init__(self, style={}, title=None):
        _style = {**style}

        self.data = []
        self.dataInfo = []
        self.index_name = []
        self.dataTransformer = []
        self.plotMethods = []
        self.option = []
        self.title = title
        self.global_title = {
            **_style.pop("title", {})
        }
        self.global_cycler = None
        self.global_limit = {}
        self.global_label = {
            "fontsize": 16,
            **_style.pop("label", {})
        }

        self.global_scale = {
            "xscale": None,
            "yscale": None
        }

        self.global_tick_params = {
            "both": {
                "axis": "both",
                "labelsize": 14,
                **_style.pop("tick", {})
            },
            "x": {
                "axis": "x",
                **_style.pop("xtick", {})
            },
            "y": {
                "axis": "y",
                **_style.pop("xtick", {})
            }
        }

        self.length = 0
        self.style = {
            "xTickRotation": 0,
            **_style
        }

    def set_title(self, ax):
        if self.title is not None:
            ax.set_title(self.title, **self.global_title)
        return ax

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
            self.__getPlotAction,
            range(self.length)
        )

        return pip(
            plot.set_cycler("default"),
            *actions,
            plot.axis_scale()({}, self.global_scale),
            plot.set_tick_parameters()({}, self.global_tick_params["both"]),
            plot.set_tick_parameters()(
                {}, {**self.global_tick_params["both"], **self.global_tick_params["x"]}),
            plot.set_tick_parameters()(
                {}, {**self.global_tick_params["both"], **self.global_tick_params["y"]}),
            plot.set_xlim()({}, self.global_limit),
            plot.set_ylim()({}, self.global_limit),
            plot.set_label()({}, self.global_label),
            self.setXaxisFormat(),
            self.set_title
        )(ax)

    def __getPlotAction(self, i):
        df = self.read(i)
        opt = self.get_option(i)

        if len(df) == 0:
            return Subplot.__noDataAx

        return lambda ax: pip(
            *[f(df, opt) for f in self.plotMethods[i]],
        )(ax)

    def read(self, i):
        """
        Indipendent from type of data source.
        """
        loader = ISubplot.IDataLoader(self.data[i], self.isTest())

        if self.isTest():
            transformers = None
        else:
            transformers = [
                self.setIndex(i),
                self.filterX(i),
                *self.dataTransformer[i]
            ]

        return loader.read(self.data[i], meta=self.dataInfo[i],
                           transformers=transformers)

    def get_option(self, i):
        if self.isTest():
            return {**self.option[i], "y": "y"}
        else:
            return self.option[i]

    def register(self, data,
                 dataInfo={},
                 plot=[],
                 option={},
                 limit={},
                 xscale=None,
                 yscale=None,
                 tick={},
                 xtick={},
                 ytick={},
                 label={},
                 cycler=None,
                 transformer=identity,
                 **_kwargs):
        """
        Parameters
        ----------
            **kwargs:
                header: int
                index: str | list[str]
                x: str
                y: str
                xlim: list|tuple
                ylim: list|tuple
                limit: dict[list|tuple]
                transformer: df -> df | list|tuple[df->df]

        """
        kwargs = {**_kwargs}
        self.data.append(data)

        _dataInfo = {**dataInfo}
        for kw in ["header"]:
            if kw in kwargs:
                _dataInfo[kw] = kwargs.pop(kw)

        self.index_name.append(kwargs.get(
            "index", []) if "index" not in _dataInfo else _dataInfo.pop("index"))

        self.dataInfo.append(_dataInfo)

        self.global_label.update(label)
        for kw in ["xlabel", "ylabel"]:
            if kw in kwargs:
                self.global_label[kw] = kwargs.pop(kw)

        self.global_scale.update({
            "xscale": xscale,
            "yscale": yscale
        })

        self.global_tick_params["both"].update(tick)
        for kw in ["labelbottom", "labeltop", "labelleft", "labelright", "bottom", "top", "left", "right"]:
            if kw in kwargs:
                self.global_tick_params["both"][kw] = kwargs.pop(kw)
        self.global_tick_params["x"].update(xtick)
        self.global_tick_params["y"].update(ytick)

        self.global_limit.update(limit)
        for kw in ["xlim", "ylim"]:
            if kw in kwargs:
                self.global_limit[kw] = kwargs.pop(kw)

        self.plotMethods.append(plot)

        _option = {**option, **kwargs}
        self.option.append(_option)

        self.global_cycler = cycler

        self.dataTransformer.append(
            transformer if type(transformer) in [list, tuple] else [transformer])

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

            limit={
                "xlim": preset["option"].get("xlim", None),
                "ylim": preset["option"].get("ylim", None),
                **arg.pop("limit", {})
            },
            label={
                "xlabel": preset["option"].get("xlabel", None),
                "ylabel": preset["option"].get("ylabel", None),
                **arg.pop("label", {})
            },
            option={**preset["option"], **option},
            ** arg
        )

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
