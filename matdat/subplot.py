from func_helper import identity, pip
import func_helper.func_helper.iterator as it
import func_helper.func_helper.dataframe as dataframe
import func_helper.func_helper.dictionary as dictionary
from . import plot
from .get_path import getFileList
from .i_subplot import ISubplot


def arg_filter(ref_keys):
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

def as_tuple(a):
    return a if type(a) is tuple else tuple(a,)


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

    def set_title(self, title):
        self.title = title
        return self

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

        actions1 = map(
            self.__getPlotAction,
            filter(lambda i: not self.is_second_axes[i], range(self.length))
        )

        ax1 = pip(
            self.plotter(actions1, self.axes_style),
            self.show_title,
            self.setXaxisFormat()
        )(ax)

        if any(self.is_second_axes):
            actions2 = map(
                self.__getPlotAction,
                filter(
                    lambda i: self.is_second_axes[i], range(self.length))
            )

            style2, _ = mix_dict(
                self.axes_style,
                self.diff_second_axes_style
            )

            _ax = self.plotter(
                [], style2
            )(ax1.twiny())

            ax2 = self.plotter(
                actions2,
                style2
            )(_ax.twinx())
            return (ax1, ax2)
        else:
            return ax1

    @staticmethod
    def Iplotter():
        def plotter(actions, style):
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
                plot.set_label()({}, style["label"]),
                plot.set_grid()({}, style["grid"])
            )
        return plotter

    def __getPlotAction(self, i):
        dfs:tuple = self.read(i)
        opt = self.get_option(i)

        if len(dfs) == 0 or all(map(lambda df: len(df) is 0, dfs)):
            return Subplot.__noDataAx

        return lambda ax: pip(
            *[f(dfs, opt) for f in self.plotMethods[i]],
        )(ax)

    def read(self, i)->tuple:
        """
        Indipendent from type of data source.
        """
        data:tuple = as_tuple(self.data[i])

        meta:tuple = as_tuple(self.dataInfo[i])

        default_transformers:tuple = self.default_transformers(i)

        data_transformers:tuple = as_tuple(self.dataTransformer[i])
        max_len = pip(
            it.mapping(len),
            it.reducing(lambda acc,e: acc if acc > e else e)(0)
        )([data,meta,default_transformers,data_transformers])

        def get_with_duplicate(it,i,default=None):
            if len(it) is 0:
                return default
            return it[i] if len(it) > i else it[-1]

        dfs = []
        for j in range(max_len):
            d = get_with_duplicate(data,j,{})
            m = get_with_duplicate(meta,j,{})
            def_trans=get_with_duplicate(default_transformers,j,[])
            trans = get_with_duplicate(data_transformers,j,[])

            loader = ISubplot.IDataLoader(d, self.isTest())

            if self.isTest():
                transformers = None
            else:
                transformers = def_trans + trans

            dfs.append(loader.read(d, meta=m,
                             transformers=transformers))
        return tuple(dfs)

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

        data_len = len(self.data[i]) if type(self.data[i]) is tuple else 1

        return tuple([filterX] for i in range(data_len))

    def get_option(self, i):
        if self.isTest():
            return {**self.option[i], "y": "y"}
        else:
            return self.option[i]

    def add(self, *arg, **kwargs):
        "ailias of register()"
        return self.register(*arg, **kwargs)

    def register(self, data={},
                 dataInfo={},
                 index=None,
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
                 grid={},
                 cycler=None,
                 transformer=identity,
                 within_xlim=False,
                 second_axis=False,
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

        # index name of data source
        self.index_name.append(index)
        self.dataInfo.append(dataInfo)

        update_axes_style = dictionary.mix(
            {
                "label": dictionary.mix(
                    kwargs.pop("label") if "label" in kwargs else {},
                    {"xlabel": xlabel} if xlabel else {},
                    {"ylabel": ylabel} if ylabel else {}
                ),
                "scale": {
                    "xscale": xscale,
                    "yscale": yscale
                },
                "tick": dictionary.mix(
                    tick,
                    arg_filter([
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

    def tee(self,
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
            index=preset.get("index",None),
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
