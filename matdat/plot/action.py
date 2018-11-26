import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms
from typing import Union, List, Tuple,TypeVar, Callable, NewType, Optional
from func_helper import pip
import func_helper.func_helper.iterator as it

DataSource = Union[dict, pd.DataFrame, np.ndarray]
Ax = NewType("Ax", [plt.subplot])
AxPlot = Callable[[Ax], Ax]
PlotAction = Callable[..., AxPlot]


def plot_action(plotter: PlotAction, arg_kwarg_generator, arg_names, default_kwargs={}):
    """
    Generate plot action by hashable object and some parameters, which takes
        matplotlib.pyplot.Axes.subplot and return it.

    When some parameters are given as list, duplicate the other parameters
        and make multiple plots.

    Parameters
    ----------
    arg_kwarg_generator: pandas.DataFrame, dict, dict -> list[tuple[list,dict]]
    arg_filter: dict -> dict
    kwarg_filter: dict -> dict
    plotter: arg,kwargs -> ax -> ax
    default: dict

    Return
    ------
    callable: (kwargs -> df, dict, kwargs) -> (ax -> ax)
    """
    arg_filter = get_values_by_keys(arg_names, None)
    kwarg_filter = filter_dict(default_kwargs.keys())

    def presetting(setting={}, **setting_kwargs):
        def set_data(data_source: DataSource, option: dict={}, **kwargs):
            """
            Parameters
            ----------
            df: pandas.DataFrame | dict
            option: dict, optional
                {
                    "x" : "x_name",
                    "y" : ["y1", "y2"],
                    "ylim" : (None,10),
                    "ylabel" : "Y",
                    "linewidth" : [1,1.5]
                }
            kwargs: parameters corresponding to items of option.
            """
            list_of_entry = to_flatlist(
                {**default_kwargs, **setting, **setting_kwargs, **option, **kwargs})
            # print(list_of_entry)

            arg_and_kwarg = arg_kwarg_generator(
                as_DataFrame(data_source),
                list(map(arg_filter, list_of_entry)),
                list(map(kwarg_filter, list_of_entry))
            )

            # return plot action
            return lambda ax: it.reducing(
                lambda ax, e: plotter(*e[0], **e[1])(ax))(ax)(arg_and_kwarg)
        return set_data
    return presetting


def as_DataFrame(d: DataSource) -> pd.DataFrame:
    if type(d) in [pd.DataFrame, pd.Series]:
        return d
    elif type(d) in [list, dict, np.ndarray]:
        return pd.DataFrame(d)
    else:
        raise TypeError(f"{type(d)} is not available for data source.")


def generate_arg_and_kwags(arg_func):
    """
    Setup positional arguments and keyword arguments for plotter.
    Positional arguments can be preprocessed by arg_func.
    """
    def gen_func(
        df: DataSource,
        option: List[list],
        style: List[dict]
    )->List[Tuple[list, dict]]:

        if len(option) != len(style):
            raise SystemError("option and style must be same size list.")

        arg_and_kwarg = []
        for o, s in zip(option, style):
            arg = [df, *o]
            kwargs = s
            arg_and_kwarg.append((arg, kwargs))
        return arg_and_kwarg
    return gen_func


def get_subset(use_index=True):
    def f(df: Union[pd.DataFrame,pd.Series], k):
        """
        Select value in hashable (pandas.DataFrame, dict, etc.)
        """
        if type(df) in [pd.DataFrame]:
            if type(k) is not list:
                return df[k] if k not in ["index", None] else df.index
            else:
                return df[k]

        elif type(df) is pd.Series:
            if k in ["index",None]:
                return df.index
            else:
                return df

        else:
            raise TypeError("df must be pandas.DataFrame or pandas.Series.")
    return f


def get_value(default=""):
    def f(_, k, v):
        """
        Return value.
        """
        return v if v is not None else default
    return f


def is_iterable(o):
    return type(o) in [list, tuple]


def to_flatlist(d: dict) -> List[dict]:
    """
    Usage
    -----
    d = {
        "x" : (0,1,2),
        "y" : [1,2],
        "z" : 0
    }

    to_flatlist(d) is...
    [
        {"x" : 0, "y" : [1,2], "z" : 0},
        {"x" : 1, "y" : [1,2], "z" : 0},
        {"x" : 2, "y" : [1,2], "z" : 0}
    ]

    """
    def value_to_list(d: dict) -> dict:
        return dict(it.mapping(
            lambda kv: (kv[0], kv[1]) if type(
                kv[1]) is tuple else (kv[0], [kv[1]])
        )(d.items()))

    list_dict = value_to_list(d)

    max_length = it.reducing(
        lambda acc, e: acc if acc >= len(e) else len(e)
    )(0)(list_dict.values())

    flatlist = []
    for i in range(max_length):
        new_dict = {}

        for k in list_dict.keys():
            if len(list_dict[k]) >= i+1:
                new_dict.update({(k): list_dict[k][i]})
            else:
                new_dict.update({(k): list_dict[k][-1]})

        flatlist.append(new_dict)
    return flatlist


def filter_dict(k: list) -> Callable[[dict], dict]:
    return lambda d: dict(
        filter(lambda kv: kv[0] in k, d.items())
    )


def get_values_by_keys(k: list, default=None)->Callable[[dict], list]:
    """
    Filter dictionary by list of keys.

    Parameters
    ----------
    k: list
    default: any, optional
        Set as default value for key not in dict.
        Default value is None
    """
    return lambda d: list(map(lambda key: d.get(key, default), k))

default_kwargs={}

_tick_params_each = {
    "labelsize": 12,
    "rotation" : 0,
    "which" : "both",
    "direction" : "out",
    "color" : "black",
    "labelcolor" : "black"
}

_tick_params_kwargs = {
    **_tick_params_each,
    "labelbottom": True,
    "labelleft" : True,
    "labeltop" : False,
    "labelright":False,
    "bottom" : True,
    "left" : True,
    "top" : False,
    "right":False
}



_label_kwargs = {
    "alpha" : 1,
    "color":"black",
    "family": ["Noto Sans CJK JP", "sans-serif"],
    #"fontname" : "sans-serif",
    "fontsize": 16,
    "fontstyle":"normal",

}

_grid_kwargs = {
    "color": 'gray',
    "linestyle": ':',
    "linewidth": 1,
}

_line2d_kwargs = {
    "alpha": 1,
    "marker": "",
    "markeredgecolor": None,
    "markeredgewidth": None,
    "markerfacecolor": None,
    "markerfacecoloralt": None,
    "markersize": None,
}

_line_kwargs = {
    **_line2d_kwargs,
    "c": None,
    "linestyle": "-",
    "linewidth": 1,
    "alpha": 1
}

_vhlines_kwargs = {
    "color": None,
    "linestyle": "-",
    "linewidth": 1,
    "alpha": 1
}

_scatter_kwargs = {
    "c": None,
    "s": None,
    "cmap": None,
    "norm": None,
    "vmin": None,
    "vmax": None,
    "alpha": 1,
    "marker": "o",
    "edgecolors": "face",
    "linewidth": None,
    "linestyle": "-"
}

_fill_kwargs = {
    "color": "green",
    "alpha": 0.5,
    "hatch": None
}

_velocity_kwargs = {
    "scale": 1,
    "scale_units": "y",
    "alpha": 0.3,
    "color": "gray",
    "width": 0.001,
    "headwidth": 5,
    "headlength": 10
}

_axline_kwargs = {
    "alpha" : 0.5,
    "color" : "green",
    "linewidth" : None,
    "linestyle" : "-"
}

default_kwargs.update({
    "tick_params": _tick_params_kwargs,
    "axis_label": _label_kwargs,
    "grid": _grid_kwargs,
    "line": _line_kwargs,
    "vlines": _vhlines_kwargs,
    "hlines": _vhlines_kwargs,
    "scatter": _scatter_kwargs,
    "fill": _fill_kwargs,
    "velocity" : _velocity_kwargs,
    "axline" : _axline_kwargs
})



def set_cycler(cycler=None):
    def setter(ax):
        if cycler is 'default':
            return ax
        elif cycler is None:
            return ax
        else:
            ax.set_prop_cycle(cycler)
        return ax
    return setter

def _get_lim(df:pd.DataFrame, lim_list:Optional[list]):
    try:
        if lim_list is not None and len(lim_list) >= 2:
            lim = [*lim_list]
            if lim[0] is None:
                lim[0] = np.min(df.min())
            if lim[1] is None:
                lim[1] = np.max(df.max())
            return lim
        else:
            return [
                np.min(df.min()),
                np.max(df.max())
            ]
    except:
        print(f"Failed: Set limit {lim_list}.")
        return None

def _get_lim_parameter(df:pd.DataFrame, lim_list:Optional[list]):
    if lim_list is not None and len(lim_list) >= 2:
        return lim_list
    else:
        return None

def _xlim_setter(df:pd.DataFrame,x,*arg, xlim=None,**kwargs)->AxPlot:
    """
    Parameters
    ----------
    x
    """
    lim = _get_lim_parameter(get_subset()(df,x), xlim)

    def plot(ax):
        if lim is not None:
            now_lim = ax.get_xlim()
            next_lim = [None,None]
            next_lim[0] = lim[0] if lim[0] is not None else now_lim[0]
            next_lim[1] = lim[1] if lim[1] is not None else now_lim[1]
            ax.set_xlim(next_lim)
        return ax
    return plot


def _ylim_setter(df:pd.DataFrame,y,*arg, ylim=None,**kwargs)->AxPlot:
    """
    Parameters
    ----------
    y
    """
    lim = _get_lim_parameter(get_subset()(df, y), ylim)

    def plot(ax):
        if lim is not None:
            now_lim = ax.get_ylim()
            next_lim = [None, None]
            next_lim[0] = lim[0] if lim[0] is not None else now_lim[0]
            next_lim[1] = lim[1] if lim[1] is not None else now_lim[1]
            ax.set_ylim(next_lim)
        return ax
    return plot


def set_xlim(**presetting):
    """
    Set xlim of ax.

    xlim is list of numbers.
    """
    return plot_action(
        _xlim_setter,
        generate_arg_and_kwags(get_value()),
        ["x"],
        {"xlim": None},
    )(**presetting)

def set_ylim(**presetting):
    return plot_action(
        _ylim_setter,
        generate_arg_and_kwags(get_value()),
        ["y"],
        {"ylim": None},
    )(**presetting)


def _grid_setter(*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.grid(**kwargs)
        return ax
    return plot


def set_grid(**presetting):
    return plot_action(
        _grid_setter,
        generate_arg_and_kwags(get_value()),
        [],
        _grid_kwargs
    )(**presetting)


def _tick_params_setter(df, axis, *arg, **kwargs)->AxPlot:
    def plot(ax):
        if axis is "both":
            ax.tick_params(axis=axis,**kwargs)
        else:
            ax.tick_params(axis=axis,**dict(filter(lambda kv: kv[0] in _tick_params_each,kwargs.items())))
        return ax
    return plot


def set_tick_parameters(**presetting):
    return plot_action(
        _tick_params_setter,
        generate_arg_and_kwags(get_value()),
        ["axis"],
        _tick_params_kwargs
    )(**presetting)

def _axis_scale(*arg,xscale=None,yscale=None):
    def plot(ax):
        if xscale is not None:
            ax.set_xscale(xscale)
        if yscale is not None:
            ax.set_yscale(yscale)
        return ax
    return plot

def axis_scale(**presetting):
    return plot_action(
        _axis_scale,
        generate_arg_and_kwags(get_value()),
        [],
        {"xscale":None,"yscale":None}
    )(**presetting)

def _label_setter(df: pd.DataFrame, xlabel: str, ylabel: str, *arg, **kwargs)->AxPlot:
    def plot(ax):
        if xlabel is not None:
            ax.set_xlabel(
                xlabel,
                **kwargs
            )
        if ylabel is not None:
            ax.set_ylabel(
                ylabel,
                **kwargs
            )
        return ax
    return plot


def set_label(**presetting):
    return plot_action(
        _label_setter,
        generate_arg_and_kwags(get_value("")),
        ["xlabel", "ylabel"],
        _label_kwargs
    )(**presetting)


def _line_plotter(df: pd.DataFrame, x, y, *arg, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    def plot(ax):
        ax.plot(_x, _y, **kwargs)
        return ax
    return plot


def line(**presetting):
    return plot_action(
        _line_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        _line_kwargs
    )(**presetting)


def _scatter_plotter(df: pd.DataFrame, x, y, *arg, s_name=None, c_name=None, **kwargs)->AxPlot:
    if c_name is not None:
        kwargs.update({"c": get_subset(False)(df, c_name)})
    if s_name is not None:
        kwargs.update({"s": get_subset(False)(df, s_name)})
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    def plot(ax):
        ax.scatter(_x, _y, **kwargs)
        return ax
    return plot


def scatter(**presetting):
        return plot_action(
        _scatter_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**_scatter_kwargs, "c_name": None, "s_name": None}
    )(**presetting)


def _vlines_plotter(df: pd.DataFrame, x, y, *arg, lower=0, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    def plot(ax):
        ax.vlines(
            _x, [lower for i in _x], _y, **kwargs
        )
        return ax
    return plot


def vlines(**presetting):
    return plot_action(
        _vlines_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**_vhlines_kwargs, "lower": 0}
    )(**presetting)


def _xband_plotter(df: pd.DataFrame, x, y, *arg, xlim=None, ypos=None, **kwargs)->AxPlot:

    def plot(ax):
        if ypos is None:
            return ax

        if type(ypos) not in [
            list, tuple, np.ndarray,
            pd.core.indexes.datetimes.DatetimeIndex,
            pd.core.series.Series
            ]:

            _kwargs = dict(
                filter(lambda kv: kv[0] in _axline_kwargs, kwargs.items())
            )
            ax.axhline(ypos, **_kwargs)

        elif len(ypos) <= 0:
            print("ypos must be list like object with having length >= 1.")

        else:
            ax.fill(
                [0, 1, 1, 0],
                [ypos[0], ypos[0], ypos[1], ypos[1]],
                transform = Icoordinate_transform(ax, "axes", "data"),
                **kwargs
            )
        return ax
    return plot


def _yband_plotter(df: pd.DataFrame, x, y, *arg, ylim=None, xpos=None, **kwargs)->AxPlot:

    def plot(ax):

        if xpos is None:
            return ax

        if type(xpos) not in [
            list, tuple, np.ndarray,
            pd.core.indexes.datetimes.DatetimeIndex,
            pd.core.series.Series
            ]:

            _kwargs = dict(
                filter(lambda kv: kv[0] in _axline_kwargs, kwargs.items())
            )
            ax.axvline(xpos, **_kwargs)

        elif len(xpos) <= 0:
            print("xpos must be list like object with having length >= 1.")

        else:

            ax.fill(
                [xpos[0], xpos[0], xpos[1], xpos[1]],
                [0, 1, 1, 0],
                transform=Icoordinate_transform(ax, "data", "axes"),
                **kwargs
            )
        return ax
    return plot


def xband(**presetting):
    return plot_action(
        _xband_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**_fill_kwargs, "xlim": None, "ypos": None}
    )(**presetting)

def yband(**presetting):
    return plot_action(
        _yband_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**_fill_kwargs, "ylim": None, "xpos": None}
    )(**presetting)


def _velocity_plotter(df: pd.DataFrame, x, ex, ey, *arg, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = [0. for i in _x],
    _ex = get_subset()(df, ex)
    _ey = get_subset()(df, ey)

    def plot(ax):
        ax.quiver(_x, _y, _ex, _ey, **kwargs)
        return ax
    return plot


def velocity(**presetting):
    return plot_action(
        _velocity_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "ex", "ey"],
        _velocity_kwargs
    )(**presetting)

def _box_plotter(df:pd.DataFrame,ys:Union[str,List[str]],*arg,**kwargs)->AxPlot:
    """
    Generate box plots for indicated columns.
    """
    _ys = ys if type(ys) is list else [ys]
    def plot(ax):
        ax.boxplot(
            [df[y].dropna() for y in _ys],
            labels=_ys,
            positions=range(0,len(_ys)),
            **kwargs
        )
        return ax
    return plot


_box_kwargs = {
    "vert": True,
    "notch": False,
    "sym": None,  # Symbol setting for out lier
    "whis": 1.5,
    "bootstrap": None,
    "usermedians": None,
    "conf_intervals": None,
    "widths": 0.5,
    "patch_artist": False,
    "manage_xticks": True,
    "autorange": False,
    "meanline": False,
    "zorder": None,
    "showcaps": True,
    "showbox": True,
    "showfliers": True,
    "showmeans": False,
    "capprops": None,
    "boxprops": None,
    "whiskerprops": None,
    "flierprops": None,
    "medianprops": None,
    "meanprops": None
}

default_kwargs.update({"box":_box_kwargs})

def box(**presetting):
    return plot_action(
        _box_plotter,
        generate_arg_and_kwags(get_value()),
        ["y"],
        _box_kwargs
    )(**presetting)


def Iget_factor(
    df:pd.DataFrame,
    f: Union[str,Callable[[pd.DataFrame],pd.Series]],
    factor:Optional[Union[list, Callable[[pd.DataFrame],pd.Series]]]
    )->Tuple[pd.Series, list]:
    d = f(df) if callable(f) else df[f]
    if type(factor) is list:
        return (d, factor)
    elif callable(factor):
        return factor(d)
    else:
        return (d,d.astype('category').cat.categories)

def _factor_box_plotter(df:pd.DataFrame,x,y,*arg,xfactor=None,**kwargs)->AxPlot:
    """
    Generate box plots grouped by a factor column in DataFrame.

    """
    _factor_series, _factor = Iget_factor(df,x,xfactor)
    _factor_detector = pd.Categorical(
        _factor_series, ordered=True, categories=_factor)

    _group = df.groupby(_factor_detector)
    _data_without_nan = [df.loc[_group.groups[fname]][y].dropna() for fname in _factor]

    def plot(ax):
        if len(_data_without_nan) is 0:
            print("No data for box plot")
            return ax
        ax.boxplot(
            _data_without_nan,
            labels=_factor,
            positions=range(0, len(_factor)),
            **kwargs
        )

        if kwargs.get("vert", True):
            ax.set_xticks(list(range(0, len(_factor))))
            ax.set_xticklabels(_factor)
            ax.set_xlim([-1, len(_factor)])
        else:
            ax.set_yticks(list(range(0, len(_factor))))
            ax.set_yticklabels(_factor)
            ax.set_ylim([-1, len(_factor)])
        return ax
    return plot


def factor_box(**presetting):
    return plot_action(
        _factor_box_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**_box_kwargs, "xfactor":None}
    )(**presetting)


_violin_kwargs = {
    "vert": True,
    "widths" :0.5,
    "showmeans":False,
    "showextrema":True,
    "showmedians":False,
    "points":100,
    "bw_method":None,

    "scale" : "width", # "width" | "count"

    "bodies": None,
    "cmeans": None
}
"""
https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.violin.html

bodies:{
    "facecolor" : "#2196f3",
    "edgecolor" : "#005588",
    "alpha" : 0.5
}
https://matplotlib.org/api/collections_api.html#matplotlib.collections.PolyCollection

cmeans:{
    "edgecolor",
    "linestyle",
    "linewidth",
    "alpha"
}
https://matplotlib.org/api/collections_api.html#matplotlib.collections.LineCollection
"""

default_kwargs.update({"violin":_violin_kwargs})

def _factor_violin_plotter(
    df:pd.DataFrame,x,y,*arg,
    bodies=None,
    cmeans=None,
    widths = 0.5,
    scale = "width",
    xfactor=None,
    **kwargs)->AxPlot:
    """
    factorが与えられたときはfactorでgroupbyする.
    与えられなかったときはdf[f]でgroupbyする.
    """
    _factor_series, _factor = Iget_factor(df,x,xfactor)
    _factor_detector = pd.Categorical(_factor_series,ordered=True,categories=_factor)

    _group = df.groupby(_factor_detector)
    _data_without_nan = [df.loc[_group.groups[fname]][y].dropna() for fname in _factor]

    _subset_hasLegalLength = pip(
        it.filtering(lambda iv: len(iv[1]) > 0),
        list
    )(enumerate(_data_without_nan))

    dataset = [iv[1].values for iv in _subset_hasLegalLength]
    positions = [iv[0] for iv in _subset_hasLegalLength]

    if scale is "count":
        count = [len(d) for d in dataset]
        variance = [np.var(d) for d in dataset]
        max_count = np.max(count)
        _widths = [c/(max_count) for c,v in zip(count,variance)]
    else:
        _widths = widths

    def plot(ax):
        if len(dataset) is 0:
            print("No data for violin plot")
            return ax

        parts = ax.violinplot(
            dataset=dataset,
            positions=positions,
            widths = _widths,
            **kwargs
        )

        # Customize style for each part of violine
        if bodies is not None:
            for p in parts["bodies"]:
                p.set_facecolor(bodies.get("facecolor","#2196f3"))
                p.set_edgecolor(bodies.get("edgecolor", "#005588"))
                p.set_alpha(bodies.get("alpha",0.5))

        if cmeans is not None:
                p = parts["cmeans"]
                p.set_edgecolor(cmeans.get("edgecolor", "#005588"))
                p.set_linestyle(cmeans.get("linestyle", "-"))
                p.set_linewidth(cmeans.get("linewidth",1))
                p.set_alpha(cmeans.get("alpha",0.5))

        if kwargs.get("vert",True):
            ax.set_xticks(list(range(0, len(_factor))))
            ax.set_xticklabels(_factor)
            ax.set_xlim([-1,len(_factor)])
        else:
            ax.set_yticks(list(range(0, len(_factor))))
            ax.set_yticklabels(_factor)
            ax.set_ylim([-1,len(_factor)])

        return ax
    return plot



def factor_violin(**presetting):
    """
    factor_violine
    --------------
    Plot violin plots for pandas.Series.
    The serieses are subset filtered by a factor.

    Usage
    -----
    plot.factor_violin(**preset_kwargs)(
        df,{
            "y":"column name for violin plot",
            "x":"column name for factor"
        }
    )(matplotlib.pyplot.subplot())

    Default preset_kwargs are:
        {
            "vert": True,
            "widths" :0.5,
            "showmeans":False,
            "showextrema":True,
            "showmedians":False,
            "points":100,
            "bw_method":None,
            "scale" : "width",
            "bodies": None,
            "cmeans": None
        }

    If scale is "width", each violin has the same width.
    Else of scale is "count", each violin has the width proportional
        to its data size.

    "bodies" is used for styling parts of violin.
    Default is:
        {
            "facecolor": "#2196f3",
            "edgecolor": "#005588",
            "alpha": 0.5
        }
    """

    return plot_action(
        _factor_violin_plotter,
        generate_arg_and_kwags(get_value()),
        ["x","y"],
        {**_violin_kwargs,"xfactor":None}
    )(**presetting)


def __selector_or_literal(df, s):
    if s is None:
        return df.index
    elif callable(s):
        return s(df)
    elif type(s) is list:
        return s
    elif type(s) in [int, float]:
        return [s]
    elif s in df:
        return df[s]
    else:
        return df.index


_text_kwargs={
    "horizontalalignment":'left',
    "ha":None,
    "verticalalignment":'bottom',
    "va":None,
    "color":"black",
    "family":None,
    "fontsize" :10,
    "rotation":None,
    "style":None,
    "xcoordinate":None, # "data" = None | "axes"
    "ycoordinate":None, # "data" = None | "axes"
    "wrap":False
}

default_kwargs.update({"text":_text_kwargs})

def Icoordinate_transform(ax,xcoordinate:Optional[str],ycoordinate:Optional[str]):
    """
    Select coordinate transform method for x and y axis.

    """
    return matplotlib.transforms.blended_transform_factory(
        ax.transAxes if xcoordinate is "axes" else ax.transData,
        ax.transAxes if ycoordinate is "axes" else ax.transData
    )

def _text_plotter(df:pd.DataFrame, x,y,text,*arg,
    xcoordinate=None,
    ycoordinate=None,
    **kwargs):
    _x = __selector_or_literal(df, x)
    _y = __selector_or_literal(df, y)
    _text = __selector_or_literal(df, text)

    def plot(ax):
        for x, y, t in zip(_x, _y, _text):
            transform = Icoordinate_transform(ax,xcoordinate,ycoordinate)
            ax.text(x, y, t, transform=transform, **kwargs)
        return ax
    return plot

def text(**presetting):
    return plot_action(
        _text_plotter,
        generate_arg_and_kwags(get_value()),
        ["x","y","text"],
        _text_kwargs
    )(**presetting)


_hist_kwargs = {
    "bins":None,
    "range":None,
    "density":None,
    "weights":None,
    "cumulative":False,
    "bottom":None,
    "histtype":'bar',
    "align":'mid',
    "orientation":'vertical',
    "rwidth":None,
    "log":False,
    "color":"#2196f3",
    "label":None,
    "stacked":False,
    "normed":None,
}

default_kwargs.update({"hist": _hist_kwargs})

def _hist_plotter(df:pd.DataFrame,y,*arg,**kwargs):
    _y = get_subset()(df, y)

    def plot(ax):
        ax.hist(_y,**kwargs)
        return ax
    return plot

def hist(**presetting):
    return plot_action(
        _hist_plotter,
        generate_arg_and_kwags(get_value()),
        ["y"],
        _hist_kwargs
    )(**presetting)


def _factor_bar_plotter(
    df:pd.DataFrame,
    x,  # factor1 selector
    y: str,  # stack factor selector
    agg,  # aggregate
    *arg,
    xfactor=None, # explicit factor list
    yfactor=None, # explicit factor list
    norm=False,
    vert=True,
    legend={},
    **kwargs):

    if type(y) is list:
        return _bar_plotter(df,x,y,agg,*arg,xfactor=xfactor,norm=norm,vert=vert,legend=legend,**kwargs)

    """
    1. stacking bar plotのstackしていくgroupingをつくる
    """
    stack_series, stack_factor = Iget_factor(df,y,yfactor)
    stack_group = df.groupby(
        pd.Categorical(
            stack_series,
            ordered=True,
            categories=stack_factor
        )
    )

    """
    2. stack groupごとにそれぞれfactorごとにgroupingする.
        * すべてのstack groupごとにx_factorの長さが同じである必要があるので,
          全データに基づくcommon_x_factorを記録しておく.
    3.

    ax.bar(ind, bar_lengths_for_each_x_factor)
    """

    stack_bars= []
    for stack_name in stack_factor:
        subset = df.loc[stack_group.groups[stack_name]]

        x_factor_series, x_factor = Iget_factor(subset, x, xfactor)

        x_group = subset.groupby(
            pd.Categorical(
                x_factor_series,
                ordered=True,
                categories=x_factor
            )
        )

        subset_for_x_factor = [
            subset.loc[x_group.groups[xfname]]\
            for xfname in x_factor
        ]

        stack_heights = pip(
            it.mapping(lambda df: df.agg(agg).values),
            it.mapping(lambda arr: arr[0] if len(arr) > 0 else 0 ),
            list
        )(subset_for_x_factor)

        stack_bars.append(stack_heights)

    if norm:
        sum = pip(
            it.mapping(np.sum),
            list
        )(zip(*stack_bars))

        stack_bars = pip(
            it.mapping(lambda bars: pip(
                it.mapping(lambda t: 0 if t[1] in [0,None,np.nan] else t[0]/t[1]),
                list
            )(zip(bars,sum))),
            list
        )(stack_bars)

    ind = list(range(len(x_factor)))
    plot_arg = {
        **kwargs,
        "tick_label": kwargs.get("tick_label", x_factor)
    }

    def plot(ax):
        prev_top = stack_bars[0]
        for i, bar in enumerate(stack_bars):
            if vert:
                if i is 0:
                    ax.bar(ind,bar,**plot_arg)
                else:
                    ax.bar(
                        ind, bar, bottom=prev_top, **plot_arg)
                    prev_top = [a+b for a, b in zip(prev_top, bar)]
            else:
                if i is 0:
                    ax.barh(ind,bar,**plot_arg)
                else:
                    ax.barh(
                        ind, bar, left=prev_top, **plot_arg)
                    prev_top = [a+b for a, b in zip(prev_top, bar)]


        ax.legend(stack_factor,**legend)
        """
        if vert:
            ax.set_xticks(ind)
            ax.set_xticklabels(x_factor)
            ax.set_xlim([-1,len(x_factor)])
        else:
            ax.set_yticks(ind)
            ax.set_yticklabels(x_factor)
            ax.set_ylim([-1,len(x_factor)])
        """
        return ax
    return plot


def factor_bar(**presetting):
    """
    plot.bar(**presetting)(df, option, **kwargs)(ax)

    df: dict, pandas.DataFrame, numpy.ndarray

    option: dict
        x:
        y:
        agg:
        **other_option

    presetting, other_option,kwargs:
        xfactor:
        yfactor:
        norm: bool
        vert: bool
        legend: dict
        align: str
        width:
    """
    return plot_action(
        _factor_bar_plotter,
        generate_arg_and_kwags(get_value()),
        ["x","y","agg"],
        {
            "xfactor":None,
            "yfactor":None,
            "norm":False,
            "vert":True,
            "legend":{}
        }
    )(**presetting)


def _bar_plotter(
    df: pd.DataFrame,
    x,  # factor1 selector
    y: str,  # stack factor selector
    agg,  # aggregate
    *arg,
    xfactor=None,  # explicit factor list
    norm=False,
    vert=True,
    legend={},
        **kwargs):

    stack_factor = y if type(y) is list else [y]
    stack_bars = []
    for stack_name in stack_factor:
        subset = df

        x_factor_series, x_factor = Iget_factor(subset, x, xfactor)

        x_group = subset.groupby(
            pd.Categorical(
                x_factor_series,
                ordered=True,
                categories=x_factor
            )
        )

        subset_for_x_factor = [
            subset.loc[x_group.groups[xfname]]
            for xfname in x_factor
        ]

        stack_heights = pip(
            it.mapping(lambda df: agg(df[stack_name])),
            #it.mapping(lambda arr: arr[0] if len(arr) > 0 else 0),
            list
        )(subset_for_x_factor)

        stack_bars.append(stack_heights)


    if norm:
        sum = pip(
            it.mapping(np.sum),
            list
        )(zip(*stack_bars))

        stack_bars = pip(
            it.mapping(lambda bars: pip(
                it.mapping(lambda t: 0 if t[1] in [
                           0, None, np.nan] else t[0]/t[1]),
                list
            )(zip(bars, sum))),
            list
        )(stack_bars)

    ind = list(range(len(x_factor)))
    plot_arg = {
        **kwargs,
        "tick_label": kwargs.get("tick_label", x_factor)
    }

    def plot(ax):
        prev_top = stack_bars[0]
        for i, bar in enumerate(stack_bars):
            if vert:
                if i is 0:
                    ax.bar(ind, bar, **plot_arg)
                else:
                    ax.bar(
                        ind, bar, bottom=prev_top, **plot_arg)
                    prev_top = [a+b for a, b in zip(prev_top, bar)]
            else:
                if i is 0:
                    ax.barh(ind, bar, **plot_arg)
                else:
                    ax.barh(
                        ind, bar, left=prev_top, **plot_arg)
                    prev_top = [a+b for a, b in zip(prev_top, bar)]

        ax.legend(stack_factor, **legend)
        """
        if vert:
            ax.set_xticks(ind)
            ax.set_xticklabels(x_factor)
            ax.set_xlim([-1, len(x_factor)])
        else:
            ax.set_yticks(ind)
            ax.set_yticklabels(x_factor)
            ax.set_ylim([-1, len(x_factor)])
        """
        return ax
    return plot


def bar(**presetting):
    """
    plot.bar(**presetting)(df, option, **kwargs)(ax)

    df: dict, pandas.DataFrame, numpy.ndarray

    option: dict
        x:
        y:
        agg:
        **other_option

    presetting, other_option,kwargs:
        xfactor:
        norm: bool
        vert: bool
        legend: dict
        align: str
        width:
    """
    return plot_action(
        _bar_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y", "agg"],
        {
            "width" : 0.8,
            "align" : "center",
            "xfactor": None,
            "norm": False,
            "vert": True,
            "legend": {}
        }
    )(**presetting)
