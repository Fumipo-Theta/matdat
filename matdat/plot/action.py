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
    if type(d) in [pd.DataFrame]:
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
    def f(df: pd.DataFrame, k):
        """
        Select value in hashable (pandas.DataFrame, dict, etc.)
        """
        if type(df) in [pd.DataFrame]:
            if type(k) is not list:
                return df[k] if k not in ["", "index", None] else df.index
            else:
                return df[k]
        else:
            raise TypeError("df must be pandas.DataFrame.")
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

_tick_params_kwargs = {
    "axis": "both",
    "labelsize": 12,
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
    "fontsize": 16
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
    "c": "#2196f3",
    "linestyle": "-",
    "linewidth": 1,
    "alpha": 1
}

_vhlines_kwargs = {
    "color": "#2196f3",
    "linestyle": "-",
    "linewidth": 1,
    "alpha": 1
}

_scatter_kwargs = {
    "c": "#2196f3",
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


def _tick_params_setter(*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.tick_params(**kwargs)
        return ax
    return plot


def set_tick_parameters(**presetting):
    return plot_action(
        _tick_params_setter,
        generate_arg_and_kwags(get_value()),
        [],
        _tick_params_kwargs
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
    lim = _get_lim(get_subset()(df, x), xlim)

    def plot(ax):
        if type(ypos) is not list or len(ypos) < 2:
            print("ypos must be list with having length >= 2.")
            return ax
        ax.fill(
            [lim[0], lim[1], lim[1], lim[0]],
            [ypos[0], ypos[0], ypos[1], ypos[1]],
            **kwargs
        )
        return ax
    return plot


def _yband_plotter(df: pd.DataFrame, x, y, *arg, ylim=None, xpos=None, **kwargs)->AxPlot:
    lim = _get_lim(get_subset()(df, y), ylim)

    def plot(ax):

        if xpos is None:
            return ax

        if type(xpos) is not list:
            _kwargs = dict(
                filter(lambda kv: kv[0] in _axline_kwargs, kwargs.items())
            )
            ax.axvline(xpos, **_kwargs)

        elif len(xpos) <= 0:
            print("xpos must be list like object with having length >= 1.")
            return ax

        else:
            ax.fill(
                [xpos[0], xpos[0], xpos[1], xpos[1]],
                [lim[0], lim[1], lim[1], lim[0]],
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

def _factor_box_plotter(df:pd.DataFrame,y,f,*arg,**kwargs)->AxPlot:
    """
    Generate box plots grouped by a factor column in DataFrame.

    """
    factor = df[f].cat.categories

    def plot(ax):
        ax.boxplot(
            [df[df[f] == fname][y].dropna() for fname in factor],
            labels=factor,
            positions=range(0, len(factor)),
            **kwargs
        )
        return ax
    return plot


def factor_box(**presetting):
    return plot_action(
        _factor_box_plotter,
        generate_arg_and_kwags(get_value()),
        ["y", "f"],
        _box_kwargs
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
}
"""
bodies:{
    "facecolor" : "#2196f3",
    "edgecolor" : "#005588",
    "alpha" : 0.5
}
"""

default_kwargs.update({"violin":_violin_kwargs})

def _factor_violin_plotter(
    df:pd.DataFrame,y,f,*arg,
    bodies=None,
    widths = 0.5,
    scale = "width",
    **kwargs)->AxPlot:

    factor = df[f].cat.categories
    data_without_nan = [df[df[f] == fname][y].dropna() for fname in factor]

    subset_hasLegalLength = pip(
        it.filtering(lambda iv: len(iv[1]) > 0),
        list
    )(enumerate(data_without_nan))

    dataset = [iv[1].values for iv in subset_hasLegalLength]
    positions = [iv[0] for iv in subset_hasLegalLength]

    if scale is "count":
        count = [len(d) for d in dataset]
        variance = [np.var(d) for d in dataset]
        max_count = np.max(count)
        _widths = [c/(max_count) for c,v in zip(count,variance)]
    else:
        _widths = widths

    def plot(ax):
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

        if kwargs.get("vert",True):
            ax.set_xticks(list(range(0, len(factor))))
            ax.set_xticklabels(factor)
            ax.set_xlim([-1,len(factor)])
        else:
            ax.set_yticks(list(range(0, len(factor))))
            ax.set_yticklabels(factor)
            ax.set_ylim([-1,len(factor)])

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
            "f":"column name for factor"
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


    """
    plot.text(
        dataframe,

    )
    """

    return plot_action(
        _factor_violin_plotter,
        generate_arg_and_kwags(get_value()),
        ["y","f"],
        _violin_kwargs
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

def _text_plotter(df:pd.DataFrame, xpos,ypos,text,*arg,
    xcoordinate=None,
    ycoordinate=None,
    **kwargs):
    _x = __selector_or_literal(df, xpos)
    _y = __selector_or_literal(df, ypos)
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
        ["xpos","ypos","text"],
        _text_kwargs
    )(**presetting)
