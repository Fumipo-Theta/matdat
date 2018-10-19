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

# +
import matplotlib.pyplot as plt
import func_helper.func_helper.iterator as it

import matdat.matdat.plot as plot
import pandas as pd
from func_helper import pip
# -

moc = pd.DataFrame(
    {
        "x" : [x - 5 for x in range(0,11)],
        "y" : [(x-5)**2 for x in range(0,11)],
        "z" : [(x-5)*2 for x in range(0,11)]
    }
)

pip(
    plot.scatter()(moc,{
        "y" : ["x","y","z"],
        "ylim" : (-20,20),
        "x" : "x",
        "color" : "white",
        "edgecolors" : ["red","green","blue"],
        "s" : 100,
        "linewidth" : 1,
        "linestyle" :["-","--"]
    }),
    plot.bar()(
        moc,
        {
            "lower":[0,-10]
        },
        x="x",
        y=["y","z"],
    ),
    plot.yband(xpos=[(-0.5,0.5),(1,1.5)])(
        moc,
        {
            "y":["y","z"],
            "hatch":"x"
        }
    ),
    plot.xband()(
        moc,
        {
            "x":"x",
            "y":"y",
            "ypos":(5,5.5),
            "color":"blue",
            "xlim":(-10,10)
        }
    ),
    plot.set_tick_parames()(
        moc,
        labelsize=20
    ),
    plot.set_label()(
        moc,
        ylabel="Y\nlabel",
        fontsize=24
    ),
    plot.set_xlim()(
        moc,
        x="x"
    ),
    plot.set_ylim()(
        moc,
        {
            "ylim" : (-20,30)
        }
    )
)(plt.subplot())

pip(
    plot.velocity()(
        moc,
        x="x",
        ex="y",
        ey="z",
        color="black"
    ),
    plot.set_xlim()(
        moc,
        xlim=(-5,10)
    ),
    plot.set_ylim()(
        moc,
        ylim=(-5, 20)
    )
)(plt.subplot())

plot.box(showmeans=True,meanprops=[{"marker":"o"}])(
    moc,
    y=("y","z"),
    vert=False
)(plt.subplot())

# +
print(plot.get_dict(["x","y","z"])({
    "y" : [0,1,2],
    "x" : [0,0,0],
}))

print(plot.to_flatlist(plot.get_dict(["x","y","z"])({
    "y" : [0,1,2],
    "x" : [0,0,0],
})))

# +
option = plot.to_flatlist({
    "x" : ["x","x"],
    "y" : ["y","z"]
})

style = plot.to_flatlist({
    "linewidth" : [1,2]
})

plot_settings = plot.generate_arg_and_kwags(plot.get_series)(moc, option, style)
display(plot_settings)

def plot_(plot_settings, plotter):
    def f(ax):
        for d in plot_settings:
            ax = plotter(*d[0], **d[1])(ax)
        return ax
    return f


ax = plot_(plot_settings, plot.line_plotter)(plt.subplot())

# +

ax = plot.line(linestyle=["-","--"])(moc,{
    "y" : ["x","y","z"],
    "x" : "x",
    "color" : ["red","green","blue"]
})(plt.subplot())

ax.legend()
# -

ax = plot.scatter(linestyle=["-","--"])(moc,{
    "y" : ["x","y","z"],
    #"x" : "x",
    "color" : "white",
    "edgecolors" : ["red","green","blue"],
    "s" : 100
})(plt.subplot())


