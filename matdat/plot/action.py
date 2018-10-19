import numpy as np
import pandas as pd
import func_helper.func_helper.iterator as it


def plot_action(arg_kwarg_generator, arg_filter, kwarg_filter, plotter, default={}):
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
    plotter: dict | list[dict] -> ax -> ax

    Return
    ------
    callable: (df, dict, kwargs) -> ax -> ax
    """
    def presetting(**setting):
        def set_data(df, option={}, **kwargs):
            """
            Parameters
            ----------
            df: pandas.DataFrame
            option: dict, optional
                {
                    "x" : "x_name",
                    "y" : ["y1", "y2"],
                    "ylim" : (None,10),
                    "ylabel" : "Y",
                    "linewidth" : [1,1.5]
                }
            """
            list_of_entry = to_flatlist({**default, **setting, **option,**kwargs})
            #print(list_of_entry)

            arg_and_kwarg = arg_kwarg_generator(
                df,
                list(map(arg_filter, list_of_entry)),
                list(map(kwarg_filter, list_of_entry))
            )

            return lambda ax: it.reducing(
                lambda ax, e: plotter(*e[0], **e[1])(ax))(ax)(arg_and_kwarg)
        return set_data
    return presetting

def generate_arg_and_kwags(arg_func):
    """
    Setup positional arguments and keyword arguments for plotter.
    Positional arguments can be preprocessed by arg_func.
    """
    def gen_func(df, option, style):
        opt = option if is_iterable(option) else [option]
        st = style if is_iterable(style) else [style]
        if len(opt) != len(st):
            raise SystemError("option and style must be same size list.")

        arg_and_kwarg = []
        for o, s in zip(opt, st):
            arg = []

            arg.append(df)

            for k, v in o.items():
                arg.append(arg_func(df, k, v))

            kwargs = s
            arg_and_kwarg.append((arg, kwargs))
        return arg_and_kwarg
    return gen_func


def get_series(use_index=True):
    def f(df, k, v):
        """
        Select value in hashable (pandas.DataFrame, dict, etc.)
        """
        if type(df) in [pd.DataFrame]:
            return df[v] if v not in ["", "index", None] else df.index
        elif type(df) is dict:
            return df.get(v,[])
        else:
            raise TypeError("df must be hashable.")
    return f

def get_df():
    def f(df,k,v):
        return (v,df)
    return f


def get_name(default=""):
    def f(_, k, v):
        """
        Return value.
        """
        return v if v is not None else default
    return f

def is_iterable(o):
    return type(o) in [list, tuple]


def to_flatlist(d: dict):
    """
    Usage
    -----
    d = {
        "x" : [0,1,2],
        "y" : [1,2],
        "z" : 0
    }

    to_flatlist(d) is...
    [
        {"x" : 0, "y" : 1, "z" : 0},
        {"x" : 1, "y" : 2, "z" : 0},
        {"x" : 2, "y" : 2, "z" : 0}
    ]

    """
    def value_to_list(d):
        return dict(it.mapping(
            lambda kv: (kv[0], kv[1]) if type(
                kv[1]) is list else (kv[0], [kv[1]])
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


def filter_dict(k: list):
    return lambda d: dict(
        filter(lambda kv: kv[0] in k, d.items())
    )


def get_dict(k: list, default=None):
    """
    Filter dictionary by list of keys.

    Parameters
    ----------
    k: list
    default: any, optional
        Set as default value for key not in dict.
        Default value is None
    """
    return lambda d: dict(
        map(lambda key: (key, d.get(key, default)), k)
    )


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

_line_kwargs = {
    "color": "#2196f3",
    "linestyle": "-",
    "linewidth": 1,
    "alpha": 1
}

_scatter_kwargs = {
    "color": "#2196f3",
    "s": 2,
    "alpha": 1,
    "marker": "o",
    "edgecolors": None,
    "linewidth": 1,
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

def get_lim(series, lim_tuple):
    try:
        if lim_tuple is not None and len(lim_tuple) >= 2:
            lim = []
            _lim = lim_tuple
            lim.append(_lim[0]
                       if _lim[0] != None
                       else np.min(series))
            lim.append(_lim[1]
                       if _lim[1] != None
                       else np.max(series))
            return lim
        else:
            return [
                np.min(series),
                np.max(series)
            ]
    except:
        return None


def xlim_setter(df,x,*arg, **kwargs):
    """
    Parameters
    ----------
    x
    """
    lim = get_lim(x, kwargs.get("xlim"))

    def plot(ax):
        if lim is not None:
            ax.set_xlim(lim)
        return ax
    return plot


def ylim_setter(df,y,*arg, **kwargs):
    """
    Parameters
    ----------
    y
    """
    lim = get_lim(y, kwargs.get("ylim"))

    def plot(ax):
        if lim is not None:
            ax.set_ylim(lim)
        return ax
    return plot


set_xlim = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x"]),
    filter_dict(["xlim"]),
    xlim_setter
)

set_ylim = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["y"]),
    filter_dict(["ylim"]),
    ylim_setter
)


def grid_setter(df,*arg, **kwargs):
    def plot(ax):
        ax.grid(**kwargs)
        return ax
    return plot


set_grid = plot_action(
    generate_arg_and_kwags(get_name()),
    get_dict([]),
    filter_dict(_grid_kwargs.keys()),
    grid_setter,
    _grid_kwargs
)


def tick_params_setter(df,*arg, **kwargs):
    def plot(ax):
        ax.tick_params(**kwargs)
        return ax
    return plot


set_tick_parames = plot_action(
    generate_arg_and_kwags(get_name()),
    get_dict([]),
    filter_dict(_tick_params_kwargs.keys()),
    tick_params_setter,
    _tick_params_kwargs
)


def label_setter(df,xlabel,ylabel,*arg, **kwargs):
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
    generate_arg_and_kwags(get_name()),
    get_dict(["xlabel", "ylabel"]),
    filter_dict(_label_kwargs.keys()),
    label_setter,
    _label_kwargs
)


def line_plotter(df,*arg, **kwargs):
    def plot(ax):
        ax.plot(*arg, **kwargs)
        return ax
    return plot


line = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x", "y"]),
    filter_dict(_line_kwargs.keys()),
    line_plotter,
    _line_kwargs
)


def scatter_plotter(df,*arg, **kwargs):
    def plot(ax):
        ax.scatter(*arg, **kwargs)
        return ax
    return plot


scatter = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x", "y"]),
    filter_dict(_scatter_kwargs.keys()),
    scatter_plotter,
    _scatter_kwargs
)

def bar_plotter(df,x,y,*arg,lower=0,**kwargs):
    def plot(ax):
        #lower = kwargs.pop("lower")
        ax.vlines(
            x, [lower for i in x], y, **kwargs
        )
        return ax
    return plot

bar = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x","y"]),
    filter_dict([*_line_kwargs.keys(),"lower"]),
    bar_plotter,
    {**_line_kwargs,"lower":0}
)


def xband_plotter(df,x,y,*arg,xlim=None,ypos=None,**kwargs):
    lim = get_lim(x,xlim)
    def plot(ax):
        if type(ypos) is not tuple or len(ypos) < 2:
            print("ypos must be tuple with having length >= 2.")
            return ax
        ax.fill(
            [lim[0], lim[1], lim[1], lim[0]],
            [ypos[0], ypos[0], ypos[1], ypos[1]],
            **kwargs
        )
        return ax
    return plot

def yband_plotter(df,x,y,*arg, ylim=None,xpos=None,**kwargs):
    lim=get_lim(y,ylim)
    def plot(ax):
        if type(xpos) is not tuple or len(xpos) < 2:
            print("xpos must be tuple with having length >= 2.")
            return ax
        ax.fill(
            [xpos[0],xpos[0],xpos[1],xpos[1]],
            [lim[0],lim[1],lim[1],lim[0]],
            **kwargs
        )
        return ax
    return plot


xband = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x", "y"]),
    filter_dict([*_fill_kwargs.keys(), "xlim", "ypos"]),
    xband_plotter,
    {**_fill_kwargs, "xlim": None, "ypos": None}
)

yband = plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x","y"]),
    filter_dict([*_fill_kwargs.keys(),"ylim","xpos"]),
    yband_plotter,
    {**_fill_kwargs,"ylim":None,"xpos":None}
)

def velocity_plotter(df,x,ex,ey,*arg,**kwargs):
    def plot(ax):
        _y = [0. for i in x]
        #ax.plot(x, _y, color="gray")
        ax.quiver(x, _y, ex, ey, **kwargs)
        return ax
    return plot

velocity=plot_action(
    generate_arg_and_kwags(get_series()),
    get_dict(["x","ex","ew"]),
    filter_dict(_velocity_kwargs.keys()),
    velocity_plotter,
    _velocity_kwargs
)

def box_plotter(df,ys,*arg,**kwargs):
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
    generate_arg_and_kwags(get_name()),
    get_dict(["y"]),
    filter_dict(_box_kwargs.keys()),
    box_plotter,
    _box_kwargs
)

def factor_box_plotter(df,y,f,*arg,**kwargs):
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
    generate_arg_and_kwags(get_name()),
    get_dict(["y","f"]),
    filter_dict(_box_kwargs.keys()),
    factor_box_plotter,
    _box_kwargs
)
