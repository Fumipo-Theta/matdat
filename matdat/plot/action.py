import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms
from typing import Union, List, Tuple, TypeVar, Callable, NewType, Optional
from func_helper import pip
import func_helper.func_helper.iterator as it
from func_helper.func_helper.iterator import DuplicateLast

DataSource = Union[dict, pd.DataFrame, pd.Series]
Ax = matplotlib.axes._subplots.Axes
AxPlot = Callable[[Ax], Ax]
PlotAction = Callable[[], AxPlot]
SetData = Callable[[DataSource, dict], AxPlot]
Presetting = Callable[[dict], SetData]
Scalar = Union[int, float]
Selector = Optional[Union[Scalar, str, Callable[[DataSource], DataSource]]]
LiteralOrSequence = Optional[Union[int, float, str, list, tuple, DataSource]]
LiteralOrSequencer = Optional[Union[LiteralOrSequence,
                                    Callable[[DataSource], DataSource]]]


def plot_action(plotter: PlotAction, arg_names: List[str], default_kwargs: dict={})->Presetting:
    """
    Generate plot action by hashable object and some parameters, which takes
        matplotlib.pyplot.Axes.subplot and return it.

    When some parameters are given as list, duplicate the other parameters
        and make multiple plots.

    Parameters
    ----------
    plotter: *arg,**kwargs -> ax -> ax
    default: dict

    Return
    ------
    callable: (kwargs -> df, dict, kwargs) -> (ax -> ax)
    """
    arg_filter = get_values_by_keys(["data"]+arg_names, None)
    kwarg_filter = filter_dict(default_kwargs.keys())

    def presetting(setting: dict={}, **setting_kwargs)->SetData:
        def set_data(data_source: DataSource, option: dict={}, **option_kwargs)->AxPlot:
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
                {"data": data_source, **default_kwargs, **setting, **setting_kwargs, **option, **option_kwargs})
            # print(list_of_entry)

            arg_and_kwarg = generate_arg_and_kwags()(
                # as_DataFrame(data_source),
                # data_source,
                list(map(arg_filter, list_of_entry)),
                list(map(kwarg_filter, list_of_entry))
            )

            # return plot action
            return lambda ax: it.reducing(
                lambda acc, e: plotter(*e[0], **e[1])(acc))(ax)(arg_and_kwarg)
        return set_data
    return presetting


def as_DataFrame(d: DataSource) -> pd.DataFrame:
    if type(d) in [pd.DataFrame, pd.Series]:
        return d
    elif type(d) in [list, dict]:
        return pd.DataFrame(d)
    else:
        raise TypeError(f"{type(d)} is not available for data source.")


def generate_arg_and_kwags():
    """
    Setup positional arguments and keyword arguments for plotter.
    """
    def gen_func(
        # df: DataSource,
        option: List[list],
        style: List[dict]
    )->List[Tuple[list, dict]]:

        if len(option) != len(style):
            raise SystemError("option and style must be same size list.")

        arg_and_kwarg = []
        for o, s in zip(option, style):
            arg = [*o]
            kwargs = s
            arg_and_kwarg.append((arg, kwargs))
        return arg_and_kwarg
    return gen_func


def get_subset(use_index=True)\
        ->Callable[[DataSource, Selector], DataSource]:
    """

    """
    def f(df: DataSource, k: Selector)->DataSource:
        """
        Select value in hashable (pandas.DataFrame, dict, etc.)
        """
        if type(df) is pd.DataFrame:
            if k in ["index", None]:
                return df.index
            elif type(k) is str:
                return df[k]
            elif type(k) in [int, float]:
                return k
            elif callable(k):
                return k(df)
            else:
                return df[k]

        elif type(df) is pd.Series:
            if k in ["index", None]:
                return df.index
            elif callable(k):
                return k(df)
            elif type(k) in [int, float]:
                return k
            else:
                return df

        elif type(df) is dict:
            if type(k) is str:
                return df.get(k, [])
            elif callable(k):
                return k(df)
            elif type(k) in [int, float]:
                return k
            else:
                return df

        else:
            # print(df)
            raise TypeError("df must be pandas.DataFrame or pandas.Series.")
    return f


def get_literal_or_series(input: LiteralOrSequencer, df: DataSource)->LiteralOrSequence:

    if callable(input):
        return input(df)
    else:
        return input


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
    def to_duplicate(d: dict) -> dict:
        return dict(it.mapping(
            lambda kv: (kv[0], kv[1]) if type(
                kv[1]) is DuplicateLast else (kv[0], DuplicateLast(kv[1]))
        )(d.items()))

    list_dict = to_duplicate(d)

    max_length = it.reducing(
        lambda acc, e: acc if acc >= len(e) else len(e)
    )(0)(list_dict.values())

    flatlist = []
    for i in range(max_length):
        new_dict = {}

        for k in list_dict.keys():
            new_dict.update({(k): list_dict[k][i]})

        flatlist.append(new_dict)
    return flatlist


def filter_dict(k: list) -> Callable[[dict], dict]:
    return lambda d: dict(
        filter(lambda kv: (kv[0] in k) and kv[1] is not None, d.items())
    )


def translate_table(table_dict: dict):
    return lambda d: {table_dict.get(k, k): v for k, v in d.items()}


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


def Iget_factor(
    df: pd.DataFrame,
    f: Union[str, Callable[[pd.DataFrame], pd.Series]],
    factor: Optional[Union[list, Callable[[pd.DataFrame], pd.Series]]]
)->Tuple[pd.Series, list]:
    d = f(df) if callable(f) else df[f]
    if type(factor) is list:
        return (d, factor)
    elif callable(factor):
        return factor(d)
    else:
        return (d, d.astype('category').cat.categories)


def selector_or_literal(df, s):
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


def Icoordinate_transform(ax, xcoordinate: Optional[str], ycoordinate: Optional[str]):
    """
    Select coordinate transform method for x and y axis.

    """
    return matplotlib.transforms.blended_transform_factory(
        ax.transAxes if xcoordinate is "axes" else ax.transData,
        ax.transAxes if ycoordinate is "axes" else ax.transData
    )


default_kwargs = {}

_tick_params_each = {
    "labelsize": 12,
    "rotation": 0,
    "which": "both",
    "direction": "in",
    "color": "black",
    "labelcolor": "black"
}

_tick_params_kwargs = {
    **_tick_params_each,
    "labelbottom": None,
    "labelleft": None,
    "labeltop": None,
    "labelright": None,
    "bottom": None,
    "left": None,
    "top": None,
    "right": None
}


_label_kwargs = {
    "alpha": 1,
    "color": "black",
    "family": ["Noto Sans CJK JP", "sans-serif"],
    # "fontname" : "sans-serif",
    "fontsize": 16,
    "fontstyle": "normal",

}

_line2d_kwargs = {
    "alpha": 1,
    "marker": "",
    "markeredgecolor": None,
    "markeredgewidth": None,
    "markerfacecolor": None,
    "markerfacecoloralt": None,
    "markersize": None,
    "linestyle": None,
    "linewidth": None,
    "color": None,
}

_grid_kwargs: dict = {
    "axis": None,
    **_line2d_kwargs,
    "color": 'gray',
    "linestyle": ':',
    "linewidth": 1,
}

_line_kwargs = {
    **_line2d_kwargs,
    "linestyle": "-",
    "linewidth": 1,
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
    "cmap": None,
    "alpha": 0.5,
    "facecolor": None,
    "hatch": None,
}

_quiver_kwargs = {
    "scale": 1,
    "scale_units": "dots",
    "alpha": 1,
    "color": "black",
    "width": 1,
    "headwidth": 0.1,
    "headlength": 0.2
}


_axline_kwargs = {
    **_line2d_kwargs,
    "alpha": 0.5,
    "color": "green",
    "linewidth": None,
    "linestyle": "-"
}

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

_violin_kwargs = {
    "vert": True,
    "widths": 0.5,
    "showmeans": False,
    "showextrema": True,
    "showmedians": False,
    "points": 100,
    "bw_method": None,

    "scale": "width",  # "width" | "count"

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

_text_kwargs = {
    "ha": 'left',
    "va": 'bottom',
    "color": "black",
    "family": None,
    "fontsize": 10,
    "rotation": None,
    "style": None,
    "xcoordinate": None,  # "data" = None | "axes"
    "ycoordinate": None,  # "data" = None | "axes"
    "wrap": False
}

_hist_kwargs = {
    "bins": None,
    "range": None,
    "density": None,
    "weights": None,
    "cumulative": False,
    "bottom": None,
    "histtype": 'bar',
    "align": 'mid',
    "orientation": 'vertical',
    "rwidth": None,
    "log": False,
    "color": "#2196f3",
    "label": None,
    "stacked": False,
    "normed": None,
}

_bar_kwargs = {
    "norm": False,
    "vert": True,
    # "width": 0.8,
    "align": "center",
}


default_kwargs.update({
    "tick_params_each": _tick_params_each,
    "tick_params": _tick_params_kwargs,
    "axis_label": _label_kwargs,
    "grid": _grid_kwargs,
    "line": _line_kwargs,
    "vlines": _vhlines_kwargs,
    "hlines": _vhlines_kwargs,
    "scatter": _scatter_kwargs,
    "fill": _fill_kwargs,
    "quiver": _quiver_kwargs,
    "axline": _axline_kwargs,
    "box": _box_kwargs,
    "violin": _violin_kwargs,
    "text": _text_kwargs,
    "hist": _hist_kwargs,
    "bar": _bar_kwargs,
})


def _annotate_plotter(df, from_pos, to_pos, text, *arg, textdict={}, **kwargs) -> AxPlot:
    def plot(ax):

        return ax
    return plot


def annotate(**presetting):
    return plot_action(
        _annotate_plotter,
        ["from_pos", "to_pos", "text"],
        {**_quiver_kwargs, "textdict": _text_kwargs}
    )(**presetting)
