import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union, List, Tuple,TypeVar, Callable, NewType
import func_helper.func_helper.iterator as it

DataSource = Union[dict,pd.DataFrame,np.ndarray]
Ax = NewType("Ax", [plt.subplot])
AxPlot = Callable[[Ax], Ax]
PlotAction = Callable[..., AxPlot]

def plot_action( plotter:PlotAction, arg_kwarg_generator, arg_names,default_kwargs={}):
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

    def presetting(**setting):
        def set_data(data_source: DataSource, option:dict={}, **kwargs):
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
            list_of_entry = to_flatlist({**default_kwargs, **setting, **option,**kwargs})
            #print(list_of_entry)


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
    elif type(d) in [list,dict,np.ndarray]:
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
    def f(df:pd.DataFrame, k):
        print(k)
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


def filter_dict(k: list) -> Callable[[dict],dict]:
    return lambda d: dict(
        filter(lambda kv: kv[0] in k, d.items())
    )


def get_values_by_keys(k: list, default=None)->Callable[[dict],list]:
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



_tick_params_kwargs = {
    "axis": "both",
    "labelsize": 12
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
    "alpha" : 1,
    "marker" : "",
    "markeredgecolor" :None,
    "markeredgewidth" : None,
    "markerfacecolor" : None,
    "markerfacecoloralt" : None,
    "markersize" : None,
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
    "cmap" : None,
    "norm" : None,
    "vmin" : None,
    "vmax" : None,
    "alpha": 1,
    "marker": "o",
    "edgecolors": "face",
    "linewidth": None,
    "linestyle": "-"
}

_fill_kwargs={
    "color": "green",
    "alpha": 0.5,
    "hatch":None
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

def get_lim(df:pd.DataFrame, lim_list:Union[list,None]):
    try:
        if lim_list is not None and len(lim_list) >= 2:
            lim = []
            _lim = list(lim_list)
            lim.append(_lim[0]
                       if _lim[0] != None
                       else np.min(df.min()))
            lim.append(_lim[1]
                       if _lim[1] != None
                       else np.max(df.max()))
            return lim
        else:
            return [
                np.min(df.min()),
                np.max(df.max())
            ]
    except:
        print("Failed: Set limit.")
        return None


def xlim_setter(df:pd.DataFrame,x,*arg, **kwargs)->AxPlot:
    """
    Parameters
    ----------
    x
    """
    lim = get_lim(get_subset()(df,x), kwargs.get("xlim"))

    def plot(ax):
        if lim is not None:
            ax.set_xlim(lim)
        return ax
    return plot


def ylim_setter(df:pd.DataFrame,y,*arg, **kwargs)->AxPlot:
    """
    Parameters
    ----------
    y
    """
    lim = get_lim(get_subset()(df, y), kwargs.get("ylim"))

    def plot(ax):
        if lim is not None:
            ax.set_ylim(lim)
        return ax
    return plot


set_xlim = plot_action(
    xlim_setter,
    generate_arg_and_kwags(get_value()),
    ["x"],
    {"xlim":None},
)

set_ylim = plot_action(
    ylim_setter,
    generate_arg_and_kwags(get_value()),
    ["y"],
    {"ylim":None},
)


def grid_setter(df:pd.DataFrame,*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.grid(**kwargs)
        return ax
    return plot


set_grid = plot_action(
    grid_setter,
    generate_arg_and_kwags(get_value()),
    [],
    _grid_kwargs
)


def tick_params_setter(df:pd.DataFrame,*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.tick_params(**kwargs)
        return ax
    return plot


set_tick_parames = plot_action(
    tick_params_setter,
    generate_arg_and_kwags(get_value()),
    [],
    _tick_params_kwargs
)


def label_setter(df:pd.DataFrame,xlabel:str,ylabel:str,*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.set_xlabel(
            xlabel,
            **kwargs
        )

        ax.set_ylabel(
            ylabel,
            **kwargs
        )
        return ax
    return plot


set_label = plot_action(
    label_setter,
    generate_arg_and_kwags(get_value()),
    ["xlabel", "ylabel"],
    _label_kwargs
)


def line_plotter(df:pd.DataFrame,x,y,*arg, **kwargs)->AxPlot:
    _x = get_subset()(df,x)
    _y = get_subset()(df,y)
    def plot(ax):
        ax.plot(_x,_y, **kwargs)
        return ax
    return plot


line = plot_action(
    line_plotter,
    generate_arg_and_kwags(get_value()),
    ["x", "y"],
    _line_kwargs
)


def scatter_plotter(df:pd.DataFrame,x,y,*arg, s_name=None, c_name=None,**kwargs)->AxPlot:
    if c_name is not None:
        kwargs.update({"c":get_subset(False)(df,c_name)})
    if s_name is not None:
        kwargs.update({"s":get_subset(False)(df,s_name)})
    _x = get_subset()(df,x)
    _y = get_subset()(df,y)
    def plot(ax):
        ax.scatter(_x,_y, **kwargs)
        return ax
    return plot


scatter = plot_action(
    scatter_plotter,
    generate_arg_and_kwags(get_value()),
    ["x", "y"],
    {**_scatter_kwargs,"c_name":None,"s_name":None}
)

def vlines_plotter(df:pd.DataFrame,x,y,*arg,lower=0,**kwargs)->AxPlot:
    _x = get_subset()(df,x)
    _y = get_subset()(df,y)
    def plot(ax):
        ax.vlines(
            _x, [lower for i in _x], _y, **kwargs
        )
        return ax
    return plot

vlines = plot_action(
    vlines_plotter,
    generate_arg_and_kwags(get_value()),
    ["x","y"],
    {**_vhlines_kwargs,"lower":0}
)


def xband_plotter(df:pd.DataFrame,x,y,*arg,xlim=None,ypos=None,**kwargs)->AxPlot:
    lim = get_lim(get_subset()(df, x),xlim)
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

def yband_plotter(df:pd.DataFrame,x,y,*arg, ylim=None,xpos=None,**kwargs)->AxPlot:
    lim=get_lim(get_subset()(df,y),ylim)
    def plot(ax):
        if type(xpos) is not list or len(xpos) < 2:
            print("xpos must be list with having length >= 2.")
            return ax
        ax.fill(
            [xpos[0],xpos[0],xpos[1],xpos[1]],
            [lim[0],lim[1],lim[1],lim[0]],
            **kwargs
        )
        return ax
    return plot


xband = plot_action(
    xband_plotter,
    generate_arg_and_kwags(get_value()),
    ["x", "y"],
    {**_fill_kwargs, "xlim": None, "ypos": None}
)

yband = plot_action(
    yband_plotter,
    generate_arg_and_kwags(get_value()),
    ["x","y"],
    {**_fill_kwargs,"ylim":None,"xpos":None}
)

def velocity_plotter(df:pd.DataFrame,x,ex,ey,*arg,**kwargs)->AxPlot:
    _x=get_subset()(df,x)
    _y = [0. for i in x],
    _ex = get_subset()(df,ex)
    _ey = get_subset()(df,ey)
    def plot(ax):
        #ax.plot(x, _y, color="gray")
        ax.quiver(_x, _y, _ex, _ey, **kwargs)
        return ax
    return plot

velocity=plot_action(
    velocity_plotter,
    generate_arg_and_kwags(get_value()),
    ["x","ex","ew"],
    _velocity_kwargs
)

def box_plotter(df:pd.DataFrame,ys,*arg,**kwargs)->AxPlot:
    def plot(ax):
        ax.boxplot(
            [df[y].dropna() for y in ys],
            labels=ys,
            positions=range(0,len(ys)),
            **kwargs
        )
        return ax
    return plot

_box_kwargs={
    "vert" : True,
    "notch":False,
    "sym" : None, # Symbol setting for out lier
    "whis": 1.5,
    "bootstrap" : None,
    "usermedians" : None,
    "conf_intervals" : None,
    "widths" : 0.5,
    "patch_artist" : False,
    "manage_xticks": True,
    "autorange" : False,
    "meanline" : False,
    "zorder" : None,
    "showcaps" : True,
    "showbox" : True,
    "showfliers" : True,
    "showmeans" : False,
    "capprops" : None,
    "boxprops" : None,
    "whiskerprops" : None,
    "flierprops" : None,
    "medianprops" : None,
    "meanprops" : None
}

box=plot_action(
    box_plotter,
    generate_arg_and_kwags(get_value()),
    ["y"],
    _box_kwargs
)

def factor_box_plotter(df:pd.DataFrame,y,f,*arg,**kwargs)->AxPlot:
    factor = df[f].cat.categories
    def plot(ax):
        ax.boxplot(
            [df[df[f] == fname][y].dropna() for fname in factor],
            labels = factor,
            positions=range(0, len(factor)),
            **kwargs
        )
        return ax
    return plot

factor_box = plot_action(
    factor_box_plotter,
    generate_arg_and_kwags(get_value()),
    ["y","f"],
    _box_kwargs
)
