from func_helper import identity, pip
import func_helper.func_helper.iterator as it
import func_helper.func_helper.dataframe as dataframe
import func_helper.func_helper.dictionary as dictionary
from . import plot
from .get_path import getFileList, PathList
from .i_subplot import ISubplot
import pandas as pd
from typing import List, Tuple, Callable, Union, Optional, TypeVar
from func_helper.func_helper.iterator import DuplicateLast as Duplicated


DataSource = Union[dict, pd.DataFrame, pd.Series, PathList]
Ax = plot.Ax
AxPlot = plot.AxPlot
PlotAction = Callable[..., AxPlot]
DataTransformer = Callable[[pd.DataFrame], pd.DataFrame]
T = TypeVar("T")


def filter_dict(ref_keys):
    return lambda dictionary: dict(filter(lambda kv: kv[0] in ref_keys, dictionary.items()))


def mix_dict(target: dict, mix_dict: dict, consume: bool=False)->dict:
    d = {}
    for key in target.keys():
        if type(target[key]) is dict:
            d[key] = {
                **target[key], **(mix_dict.pop(key, {}) if consume else mix_dict.get(key, {}))}
        else:
            d[key] = mix_dict.pop(
                key, target[key]) if consume else mix_dict.get(key, target[key])
    return d, mix_dict


def wrap_by_duplicate(a: Union[T, Duplicated])->Union[Duplicated]:
    """
    Wrap not tuple parameter by tuple.
    """
    return a if type(a) is Duplicated else Duplicated(a)


class Subplot(ISubplot):
    """
    Csvファイルを読み込み, その中のデータを変形し, プロットするメソッドを返す.
    Figureオブジェクトに登録することで最終的にプロットが作成される.

    Example
    -------
    fig=Figure():

    fig.add_subplot(
        Subplot.create(axStyle)\
            .register(
                data=getFileList(pattern1,pattern2,...)(directory),
                dataInfo={
                    "header": 3
                },
                plot=[plot.scatter(),plot.line()],
                xlim=["2018/08/10 00:00:00","2018/08/19 00:00:00"],
                y="Salinity",
                ylim=[25,35],
                ylabel="Salinity"
            )
    )
    """
    @staticmethod
    def create(*style_dict, **style):
        subplot = Subplot(*style_dict, **style)
        return subplot

    @staticmethod
    def create_empty_space():
        return Subplot().add(
            plot=[lambda df, opt: Subplot.__noDataAx]
        )

    def __new__(cls, *arg, **kwargs):
        return super().__new__(cls)

    def __init__(self, *style_dict, **style):

        self.data = []
        self.dataInfo = []
        self.index_name = []
        self.dataTransformer = []
        self.plotMethods = []
        self.option = []
        self.is_second_axes = []
        self.filter_x = False
        self.title = None

        default_axes_style = {
            "title": {
                "fontsize": 16
            },
            "cycler": None,
            "xlim": [],
            "ylim": [],
            "label": {
                "fontsize": 16,
            },
            "xlabel_setting": {},
            "ylabel_setting": {},
            "scale": {
                "xscale": None,
                "yscale": None,
            },
            "tick": {
                "labelsize": 14,
            },
            "xtick": {},
            "ytick": {},
            "grid": {},
            "style": {}
        }

        _style, _ = mix_dict(style_dict[0], style) if len(
            style_dict) > 0 else mix_dict(style, {})
        self.axes_style, rest_style = mix_dict(
            default_axes_style, _style, True)
        self.axes_style["style"].update({
            "xTickRotation": 0,
            **rest_style
        })

        self.diff_second_axes_style = {
            "title": {},
            "cycler": None,
            "xlim": [],
            "ylim": [],
            "label": {},
            "xlabel_setting": {},
            "ylabel_setting": {},
            "scale": {},
            "tick": {},
            "xtick": {},
            "ytick": {},
            "grid": {},
            "style": {}
        }

        # print(self.axes_style)

        self.length = 0
        self.plotter = Subplot.Iplotter()

    def set_title(self, title=""):
        self.title = title
        return self

    def get_first_axis_style(self)->dict:
        return self.axes_style

    def get_second_axis_style(self)->dict:
        return mix_dict(
            self.axes_style,
            self.diff_second_axes_style
        )[0]

    def show_title(self, ax):
        if self.title is not None:
            ax.set_title(self.title, **self.axes_style.get("title", {}))
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

        first_plot_actions = map(
            self.__getPlotAction,
            filter(lambda i: not self.is_second_axes[i], range(self.length))
        )

        first_axis_style = self.get_first_axis_style()

        ax1 = pip(
            self.plotter(first_plot_actions, first_axis_style),
            self.show_title,
            self.setXaxisFormat()
        )(ax)

        if any(self.is_second_axes):
            second_axis_actions = map(
                self.__getPlotAction,
                filter(
                    lambda i: self.is_second_axes[i], range(self.length))
            )

            second_xaxis_style = {**self.get_second_axis_style(), "ylim": []}
            second_yaxis_style = {**self.get_second_axis_style(), "xlim": []}

            # A hack for changing the first and the second axis limits independently.
            ax2 = pip(
                lambda ax: ax.twiny(),
                self.plotter([], second_xaxis_style),
                lambda ax: ax.twinx(),
                self.plotter(second_axis_actions, second_yaxis_style)
            )(ax1)

            return (ax1, ax2)
        else:
            return ax1

    @staticmethod
    def Iplotter():
        def plotter(actions, style):
            """

            """
            return pip(
                plot.set_cycler(style["cycler"]),
                *actions,
                plot.axis_scale()({}, style["scale"]),
                plot.set_tick_parameters(axis="both")(
                    {}, style["tick"]),
                plot.set_tick_parameters(axis="x")(
                    {}, {**style["tick"], **style["xtick"]}),
                plot.set_tick_parameters(axis="y")(
                    {}, {**style["tick"], **style["ytick"]}),
                plot.set_xlim()({}, {"xlim": style["xlim"]}),
                plot.set_ylim()({}, {"ylim": style["ylim"]}),
                plot.set_xlabel()(
                    {}, {**style["label"], **style["xlabel_setting"]}),
                plot.set_ylabel()(
                    {}, {**style["label"], **style["ylabel_setting"]}),
                plot.set_grid()({}, style["grid"])
            )
        return plotter

    def __getPlotAction(self, i):
        dfs: Duplicated = self.__read(i)
        opt = self.get_option(i)

        if len(dfs) == 0 or all(map(lambda df: len(df) is 0, dfs.args)):
            return Subplot.__noDataAx

        return lambda ax: pip(
            *[f(dfs, opt) for f in self.plotMethods[i]],
        )(ax)

    def __read(self, i)->Tuple[pd.DataFrame]:
        """
        Indipendent from type of data source.
        """
        data: Duplicated = wrap_by_duplicate(self.data[i])
        meta: Duplicated = wrap_by_duplicate(self.dataInfo[i])
        default_transformers: Duplicated = self.default_transformers(i)
        data_transformers: Duplicated = wrap_by_duplicate(
            self.dataTransformer[i])

        max_len = pip(
            it.mapping(len),
            it.reducing(lambda acc, e: acc if acc > e else e)(0)
        )([data, meta, default_transformers, data_transformers])

        def get_with_duplicate(it: Duplicated, i, default=None):
            if len(it) is 0:
                return default
            return it[i]

        dfs = []
        for j in range(max_len):
            d = get_with_duplicate(data, j, {})
            m = get_with_duplicate(meta, j, {})
            def_trans = get_with_duplicate(default_transformers, j, [])
            trans = get_with_duplicate(data_transformers, j, [])

            loader = ISubplot.IDataLoader(d, self.isTest())

            if self.isTest():
                transformers = None
            else:
                transformers = def_trans + trans

            dfs.append(loader.read(d, meta=m,
                                   transformers=transformers))
        return Duplicated(*dfs)

    def default_transformers(self, i)->tuple:
        def filterX(df):
            x = self.option[i].get("x", None)
            lim = self.axes_style.get("xlim")
            if len(lim) is 0 or lim is None:
                return df
            elif len(lim) is 1:
                lower = lim[0]
                upper = None
            else:
                lower, upper, *_ = lim

            return dataframe.filter_between(
                lower, upper, False, False
            )(df, x) if self.filter_x else df

        data_len = len(self.data[i]) if type(self.data[i]) is Duplicated else 1

        return Duplicated(*[[filterX] for i in range(data_len)])

    def get_option(self, i):
        if self.isTest():
            return {**self.option[i], "y": "y"}
        else:
            return self.option[i]

    def register(self, *arg, **kwargs):
        "ailias of self.add"
        return self.add(*arg, **kwargs)

    def add(self,
            data: Union[DataSource, Tuple[DataSource]]={},
            dataInfo: dict={},
            index: Optional[Union[List[str], Tuple[List[str]]]]=None,
            transformer: Union[DataTransformer, List[DataTransformer], Tuple[DataTransformer], Tuple[List[DataTransformer]]]=identity,
            plot: List[PlotAction]=[],
            option: dict={},
            xlim: Optional[list]=None,
            ylim: Optional[list]=None,
            xscale: Optional[str]=None,
            yscale: Optional[str]=None,
            tick: dict={},
            xtick: dict={},
            ytick: dict={},
            label: dict={},
            xlabel_setting: dict={},
            ylabel_setting: dict={},
            xlabel: Optional[str]=None,
            ylabel: Optional[str]=None,
            grid: dict={},
            cycler=None,
            within_xlim: bool=False,
            second_axis: bool=False,
            **_kwargs):
        """
        Set parameters for plotting.

        Parameters
        ----------
        data, optional: DataSource, Tuple[DataSource]
            Data source as pandas.DataFrame, dict, and PathLike objects or tuple of them.
            Default value is {}.
        dataInfo, optional: dict
            Dict of parameters in reading data source files.
            Keys and values must be compatible to data loader
            such as pandas.read_csv and pandas.read_excel.
            Default value is {}.
        index, optional: List[str], Tuple[List[str]]
            List of str or tuple of it for column names used as
            index of dataframe.
            When list of column names is passed, values of index is made by concatenating the columns.
            Default value is None.
        transformer, optional: DataTransformer, List[DataTransformer], Tuple[DataTransformer], Tuple[List[DataTransformer]]
            Functions for transforming dataframe object prior to plot.
        plot, optional: List[PLotAction]
            List of plot actions.
        xlim, ylim, optional: List[int,float]
            List of numbers for defining limit of xy axis.
        xscale, yscale, optional: str
            Str of type of axis scale.
            "linear", "log" can be used.
        tick, xtick, ytick, optional: dict
            Dict defining style of ticks.
        label, optional:
            Dict defining style of axis labels.
        xlabel, ylabel, optional: str
            Str for x and y label of axis.
        grid, optional: dict
            Dict defining style of grid lines.
        cycler, optional: cycler
            Cycler defining cycling style of plotted symbols.
        within_xlim, optional: bool
            Flag whether plot only data in xlim.
        second_axis, optinal: bool
            Flag for plot on second axis.

        **kwargs:
            Parameters passed to PlotActions.
            They are broad casted on all PlotActions.
        """

        kwargs = {**_kwargs}
        self.data.append(data)

        # index name of data source
        self.index_name.append(index)
        self.dataInfo.append(dataInfo)

        update_axes_style = dictionary.mix(
            {
                "label": dictionary.mix(
                    label,
                    {"xlabel": xlabel} if xlabel is not None else {},
                    {"ylabel": ylabel} if ylabel is not None else {}
                ),
                "xlabel_setting": dictionary.mix(
                    {},
                    xlabel_setting if type(xlabel_setting) is dict else {}
                ),
                "ylabel_setting": dictionary.mix(
                    {},
                    ylabel_setting if type(ylabel_setting) is dict else {}
                ),
                "scale": {
                    "xscale": xscale,
                    "yscale": yscale
                },
                "tick": dictionary.mix(
                    tick,
                    filter_dict([
                        "labelbottom",
                        "labeltop",
                        "labelleft",
                        "labelright",
                        "bottom",
                        "top",
                        "left",
                        "right"
                    ])(kwargs)
                ),
                "xtick": xtick,
                "ytick": ytick,
                "grid": grid,
            },
            kwargs.get("limit", {}),
            {"xlim": xlim} if xlim is not None else {},
            {"ylim": ylim} if ylim is not None else {},
            {"cycler": cycler} if cycler else {}
        )

        if not second_axis:
            self.axes_style, _ = mix_dict(
                self.axes_style,
                update_axes_style
            )
        else:
            self.diff_second_axes_style, _ = mix_dict(
                self.diff_second_axes_style,
                update_axes_style
            )

        # plot
        self.plotMethods.append(plot)

        # plot option
        _option = dictionary.mix(option, kwargs)
        self.option.append(_option)

        # transformer
        self.dataTransformer.append(
            transformer if type(transformer) in [list, tuple] else [transformer])

        self.filter_x = within_xlim
        self.is_second_axes.append(second_axis)

        self.length = self.length+1
        return self

    def forked(self,
               *option,
               **style_kwargs
               ):
        """
        Method for extends a subplot to the another subplot.
        Without any option, a subplot instance is copied to
        the new one.
        On the other hand, with option, part of properties of
        the old subplot can be over written.

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

        new_subplot = self.create(
            **mix_dict(self.axes_style,
                       style_kwargs)[0]
        )

        new_subplot.diff_second_axes_style = {**self.diff_second_axes_style}

        for i in range(self.length):
            new_subplot.add(
                **dictionary.mix(
                    {
                        "data": self.data[i],
                        "dataInfo": self.dataInfo[i],
                        "index": self.index_name[i],
                        "plot": self.plotMethods[i],
                        "second_axis": self.is_second_axes[i],
                        "transformer": self.dataTransformer[i],
                    },
                    self.option[i],
                    option[i] if len(option) > i and type(
                        option[i]) is dict else {},
                )
            )

        return new_subplot

    def setPreset(self, preset):
        self.preset = preset
        return self

    def usePreset(self, name, fileSelector=[], plot=[], plotOverwrite=[], option={}, **kwargs):
        preset = self.preset[name]

        return self.register(
            data=tuple(getFileList(*fileSelector)(directory)
                       for directory in preset["directory"]) if type(preset["directory"]) is tuple else getFileList(*fileSelector)(preset["directory"]),
            dataInfo=preset["dataInfo"],
            index=preset.get("index", None),
            plot=[*preset["plot"], *plot] if not plotOverwrite else plotOverwrite,

            **dictionary.mix(
                preset["option"],
                option,
                kwargs
            )
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
