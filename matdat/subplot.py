import pandas as pd
from func_helper import identity, pip
import func_helper.func_helper.dataframe as dataframe
from .plot_action import set_xlim, set_ylim, setStyle
import matdat.matdat.plot as plot
from .get_path import PathList, getFileList
from .i_subplot import ISubplot


def arg_filter(ref_keys):
    return lambda dictionary: dict(filter(lambda kv: kv[0] in ref_keys, dictionary.items()))

def mix_dict(target:dict, mix_dict:dict, consume:bool=False)->dict:
    d = {}
    for key in target.keys():
        if type(target[key]) is dict:
            d[key] = {**target[key], **(mix_dict.pop(key,{}) if consume else mix_dict.get(key,{}))}
        else:
            d[key] = mix_dict.pop(
                key, target[key]) if consume else mix_dict.get(key, target[key])
    return d, mix_dict

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
    def create(*style_dict,**style):
        subplot = Subplot(*style_dict,**style)
        return subplot

    def __init__(self, *style_dict, **style):

        self.data = []
        self.dataInfo = []
        self.index_name = []
        self.dataTransformer = []
        self.plotMethods = []
        self.option = []
        self.title = None

        default_axes_style={
            "title": {
                "fontsize" : 16
            },
            "cycler" : None,
            "xlim" : [],
            "ylim" : [],
            "label": {
                "fontsize": 16,
            },
            "scale":{
                "xscale" : None,
                "yscale" : None,
            },
            "tick": {
                "labelsize": 14,
            },
            "xtick": {},
            "ytick": {},
        }

        _style, _ = mix_dict(style_dict[0],style) if len(style_dict) > 0 else mix_dict(style,{})
        self.axes_style, rest_style = mix_dict(default_axes_style,_style, True)
        self.axes_style["style"] = {
            "xTickRotation" : 0,
            **rest_style
        }

        #print(self.axes_style)

        self.length = 0

    def set_title(self,title):
        self.title=title
        return self

    def show_title(self, ax):
        if self.title is not None:
            ax.set_title(self.title, **self.axes_style.get("title",{}))
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
            plot.set_cycler(self.axes_style["cycler"]),
            *actions,
            plot.axis_scale()({}, self.axes_style["scale"]),
            plot.set_tick_parameters(axis="both")({}, self.axes_style["tick"]),
            plot.set_tick_parameters(axis="x")(
                {}, {**self.axes_style["tick"], **self.axes_style["xtick"]}),
            plot.set_tick_parameters(axis="y")(
                {}, {**self.axes_style["tick"], **self.axes_style["ytick"]}),
            plot.set_xlim()({}, {"xlim":self.axes_style["xlim"]}),
            plot.set_ylim()({}, {"ylim":self.axes_style["ylim"]}),
            plot.set_label()({}, self.axes_style["label"]),
            self.setXaxisFormat(),
            self.show_title
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
                *self.default_transformers(i),
                *self.dataTransformer[i]
            ]

        return loader.read(self.data[i], meta=self.dataInfo[i],
                           transformers=transformers)

    def default_transformers(self,i):
        def filterX(df):
            x = self.option[i].get("x",None)
            lim = self.axes_style.get("xlim")
            if len(lim) is 0 or lim is None:
                return df
            elif len(lim) is 1:
                lim = lim + [None]

            return dataframe.filter_between(
                *lim
            )(df,x)

        return [filterX]



    def get_option(self, i):
        if self.isTest():
            return {**self.option[i], "y": "y"}
        else:
            return self.option[i]

    def add(self, *arg, **kwargs):
        "ailias of register()"
        return self.register(*arg, **kwargs)


    def register(self, data,
                 dataInfo={},
                 plot=[],
                 option={},
                 xlim=None,
                 ylim=None,
                 xscale=None,
                 yscale=None,
                 tick={},
                 xtick={},
                 ytick={},
                 xlabel=None,
                 ylabel=None,
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

        # kwargs in read data source
        _dataInfo = {**dataInfo}
        for kw in ["header"]:
            if kw in kwargs:
                _dataInfo[kw] = kwargs.pop(kw)

        # index name of data source
        self.index_name.append(kwargs.get(
            "index", []) if "index" not in _dataInfo else _dataInfo.pop("index"))
        self.dataInfo.append(_dataInfo)

        # axis label
        self.axes_style["label"].update({
            **(kwargs.pop("label") if "label" in kwargs else {}),
            **({"xlabel": xlabel} if xlabel else {}),
            **({"ylabel": ylabel} if ylabel else {})
        })

        # scale
        self.axes_style["scale"].update({
            "xscale": xscale,
            "yscale": yscale
        })

        # tick
        self.axes_style["tick"].update(
            **tick,
            **arg_filter([
                "labelbottom",
                "labeltop",
                "labelleft",
                "labelright",
                "bottom",
                "top",
                "left",
                "right"
            ])(kwargs)
        )

        self.axes_style["xtick"].update(xtick)
        self.axes_style["ytick"].update(ytick)

        # axis limit
        self.axes_style.update({
            **kwargs.get("limit",{}),
            **({"xlim":xlim} if xlim else {} ),
            **({"ylim":ylim} if ylim else {} )
        })

        # plot
        self.plotMethods.append(plot)

        # plot option
        _option = {**option, **kwargs}
        self.option.append(_option)

        # cycler
        if cycler:
            self.axes_style["cycler"] = cycler

        # transformer
        self.dataTransformer.append(
            transformer if type(transformer) in [list, tuple] else [transformer])

        self.length = self.length+1
        return self

    def tee(self,
        *option,
        **style_kwargs
        ):
        """
        Parameters
        ----------
        *option: *dict
            Keys and values must be compatible to parameters
                for register() or add() method.
        title: str
        **style_kwargs:
            Overwrite style of axes
            ----------------------
            title: dict
            cycler: cycler
            xlim: list
            ylim: list
            label: dict
            scale: dict
            tick: dict
            xtick: dict
            ytick: dict

            xTickRotation
            xFmt
        """

        new_subplot = Subplot.create(
            **{**self.axes_style,
            **style_kwargs}
        )

        for i in range(len(self.data)):
                new_subplot.add(
                    **{
                        "data" : self.data[i],
                        "dataInfo":self.dataInfo[i],
                        "index":self.index_name[i],
                        "plot": self.plotMethods[i],
                        **self.option[i],
                        **(option[i] if len(option) > i and type(option[i]) is dict else {}),
                    }
                )

        return new_subplot


    def setPreset(self, preset):
        self.preset = preset
        return self

    def usePreset(self, name, fileSelector=[], plot=[], plotOverwrite=[], option={}, **arg):
        preset = self.preset[name]
        return self.register(
            data=getFileList(*fileSelector)(preset["directory"]),
            dataInfo=preset["dataInfo"],
            plot=[*preset["plot"], *plot] if not plotOverwrite else plotOverwrite,

            **{
                **preset["option"],
                **option,
                **arg
            }
        )

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
