# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.7.0
# ---

import matplotlib.pyplot as plt
import func_helper.func_helper.iterator as it

# +
def plot_action(arg_kwarg_generator, arg_filter, kwarg_filter, plotter, default={}):
    """
    Parameters
    ----------
    arg_kwarg_generator: pandas.DataFrame, dict, dict -> list[tuple[list,dict]]
    arg_filter: dict -> dict
    kwarg_filter: dict -> dict
    plotter: dict | list[dict] -> ax -> ax

    Return
    ------
    callable: (style -> df, option) -> ax -> ax
    """
    def action(**kwargs):
        def set_data(df, option):
            """
            Parameters
            ----------
            df: pandas.DataFrame
            option: dict
                {
                    "x" : "x_name",
                    "y" : ["y1", "y2"],
                    "ylim" : [],
                    "ylabel" : "Y",
                    "linewidth" : [1,1.5]
                }
            """
            list_of_entry = to_flatlist({**default, **kwargs, **option})
            
            arg_and_kwarg = arg_kwarg_generator(
                df,
                list(map(arg_filter,list_of_entry)),
                list(map(kwarg_filter,list_of_entry))
            )
 
            return lambda ax: it.reducing(
                lambda ax, e: plotter(*e[0], **e[1])(ax))(ax)(arg_and_kwarg)
        return set_data
    return action


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
            lambda kv: (kv[0], kv[1]) if is_iterable(kv[1]) else (kv[0], [kv[1]])
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
        filter(lambda kv: kv[0] in k ,d.items())
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
        map(lambda key: (key, d.get(key,default)),k)
    )


def generate_arg_and_kwags(arg_func):
    def gen_func(df, option, style):
        opt = option if is_iterable(option) else [option]
        st = style if is_iterable(style) else [style]

        arg_and_kwarg = []
        for o,s in zip(opt,st):
            arg = []
            for k,v in o.items():
                arg.append(arg_func(df,k,v)) 
            kwargs = s
            arg_and_kwarg.append((arg, kwargs))
        return arg_and_kwarg
    return gen_func

def get_series(df,k,v):
    return df[v] if v not in ["","index",None] else df.index

def get_name(_, k, v):
    return v if v is not None else ""


def tick_params_setter(*arg, **kwargs):
    def plot(ax):
        ax.tick_params(**kwargs)
        return ax
    return plot

def label_setter(*arg,**kwargs):
    def plot(ax):
        ax.set_xlabel(
                arg[0],
                **kwargs
            )

        ax.set_ylabel(
                arg[1],
                **kwargs
            )
        return ax
    return plot
        

def line_plotter(*arg, **kwargs):
    def plot(ax):
        ax.plot(*arg, **kwargs)
        return ax
    return plot

def scatter_plotter(*arg, **kwargs):
    def plot(ax):
        ax.scatter(*arg, **kwargs)
        return ax
    return plot

tick_parames=plot_action(generate_arg_and_kwags(get_name), get_dict([]), filter_dict(["axis","labelsize"]),tick_params_setter,{
    "axis" : "both",
    "labelsize" : 12
})

set_label=plot_action(generate_arg_and_kwags(get_name), get_dict(["xlabel","ylabel"]),filter_dict(["fontsize"]),label_setter,{
    "fontsize" : 16
})

#set_label = plot_action()

line = plot_action(generate_arg_and_kwags(get_series), get_dict(["x","y"]), filter_dict(["linewidth","linestyle","color","alpha"]), line_plotter)
scatter = plot_action(generate_arg_and_kwags(get_series), get_dict(["x","y"]), filter_dict(["color",
    "s",
    "alpha",
    "marker",
    "edgecolors",
    "linewidth",
    "linestyle"]), scatter_plotter)

# +
print(get_dict(["x","y","z"])({
    "y" : [0,1,2],
    "x" : [0,0,0],
}))

print(to_flatlist(get_dict(["x","y","z"])({
    "y" : [0,1,2],
    "x" : [0,0,0],
})))
# -

import pandas as pd
from func_helper import pip

moc = pd.DataFrame(
    {
        "x" : [x - 5 for x in range(0,11)],
        "y" : [(x-5)**2 for x in range(0,11)],
        "z" : [(x-5)*2 for x in range(0,11)]
    }
)
display(moc)

# +
option = to_flatlist({
    "x" : ["x","x"],
    "y" : ["y","z"]
})

style = to_flatlist({
    "linewidth" : [1,2]
})

plot_settings = generate_arg_and_kwags(get_series)(moc, option, style)
display(plot_settings)

def plot(plot_settings, plotter):
    def f(ax):
        for d in plot_settings:
            ax = plotter(*d[0], **d[1])(ax)
        return ax
    return f


ax = plot(plot_settings, line_plotter)(plt.subplot())

# +

ax = line(linestyle=["-","--"])(moc,{
    "y" : ["x","y","z"],
    "x" : "x",
    "color" : ["red","green","blue"]
})(plt.subplot())

ax.legend()
# -

ax = scatter(linestyle=["-","--"])(moc,{
    "y" : ["x","y","z"],
    #"x" : "x",
    "color" : "white",
    "edgecolors" : ["red","green","blue"],
    "s" : 100
})(plt.subplot())

pip(
    scatter(linestyle=["-","--"])(moc,{
        "y" : ["x","y","z"],
        "x" : "x",
        "color" : "white",
        "edgecolors" : ["red","green","blue"],
        "s" : 100
    }),
    tick_parames()(
        moc,
        {
            "labelsize":20
        }
    ),
    set_label(fontsize=24)(
        moc,
        {
            "ylabel" : "Y\nlabel"
        }
    )
)(plt.subplot())
