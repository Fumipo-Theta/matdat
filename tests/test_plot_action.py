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

import matplotlib as mpl

import matplotlib.pyplot as plt
import func_helper.func_helper.iterator as it

import matdat.matdat.plot as plot
import pandas as pd
import numpy as np
from func_helper import pip
from matdat import Figure, Subplot

from cycler import cycler

# +
moc = {
        "x" : [x - 5 for x in range(0,11)],
        "y" : [(x-5)**2 for x in range(0,11)],
        "z" : [(x-5)*2 for x in range(0,11)]
    } 

moc_df = pd.DataFrame(moc)
moc_df

# +
moclist = list(
    zip([x - 5 for x in range(0,11)],
    [(x-5)**2 for x in range(0,11)],
    [(x-5)*2 for x in range(0,11)])
)


moclist_df = pd.DataFrame(moclist)
moclist_df.head(5)
# -

type(moclist_df.groupby(0))

[moc.get(k) for k in ("x","y")]

np.min([moc.get(k) for k in ("x","y")])

np.min(np.min(moc_df[list(("x","y"))]))

np.min(moc_df[list(("x"))].min())

pip(
    plot.line()(moc,{
        "x" : "x",
        "y" : ("y"),
        
    }),
    plot.scatter()(moc,{
        "y" : ("x","y","z"),
        "ylim" : [-20,20],
        "x" : "x",
        "c" : "white",
        "edgecolors" : ("red","green","blue"),
        "s" : 100,
        "linewidth" : 1,
        "linestyle" :("-","--")
    }),
    plot.vlines()(
        moc,
        {
            "lower":(0,-10)
        },
        x="x",
        y=("y","z"),
    ),
    plot.yband(xpos=([-0.5,0.5],[1,1.5]))(
        moc,
        {
            "y":["y","z"],
            "hatch":"x"
        }
    ),
    plot.yband(xpos=([-0.5,0.5],[1,1.5]))(
        moc,
        {
            "y":("y","z"),
            "color":"red"
        }
    ),
    plot.xband()(
        moc,
        {
            "x":"x",
            "y":"y",
            "ypos":[5,5.5],
            "color":"blue",
            "xlim":[None,10]
        }
    ),
    plot.set_tick_parameters()(
        moc,
        axis="x",
        labelsize=20,
        rotation=90
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
            "y":["y","z"],
            "ylim" : None
        }
    ),
    plot.axis_scale()(
        {}
    )
)(plt.subplot())

plt.plot(moc_df["x"],moc_df["y"])
plt.plot(moc_df["x"],moc_df["z"])

# +


figure = Figure()

figure.add_subplot(
    Subplot.create()\
    .register(
        moc_df,
        x="x",
        y=("y","z","x"),
        c=None,
        plot=[plot.scatter(),plot.line()]
    )
)

fig,axs = figure.show(size=(8,6))



# +

figure = Figure()

figure.add_subplot(
    Subplot.create()\
    .register(
        moc_df,
        x="x",
        y="y",
        c=None,
        plot=[plot.scatter(),plot.line()]
    )\
    .register(
        moc_df,
        x="x",
        y="z",
        c=None,
        plot=[plot.scatter()]
    )
)

fig,axs = figure.show(size=(8,6))

# -

plt.hist(moc_df["y"])


# +
ax = pip(
    plot.hist()(
        moc_df,
        y="y",
    )
)(plt.subplot())

ax.tick_params(axis="x",rotation=90)

# +
ax = pip(
    plot.velocity()(
        moc_df,
        x="x",
        ex="y",
        ey="z",
        color="black"
    ),
    plot.set_xlim()(
        moc,
        xlim=[-5,10]
    ),
    plot.set_ylim()(
        moc,
        ylim=[-5, 20]
    )
)(plt.subplot())

type(ax)
# -

plot.box(showmeans=True,meanprops=({"marker":"o"}))(
    moc_df,
    y=["y","z"],
    vert=False
)(plt.subplot())

# +
figure = Figure()

figure.add_subplot(
    Subplot.create()\
    .register(
        moc,
        x="x",
        y="z",
        s=moc["y"],
        ylim = [-10,None],
        plot=[plot.scatter()]
    )\
    .register(
        moc,
        x="x",
        y="y",
        plot=[plot.scatter(),plot.line()]
    )
)

fig, axs = figure.show(size=(8,6))
# -

ind = (0,1,2)
a = [-1,2,0]
b = np.array([2,3,1])
plt.bar(ind,a)
plt.bar(ind,b,bottom=a)

ind = (0,1,2)
a = [-1,2,0]
b = np.array([2,3,1])
c = np.array([1,1,1])
plt.barh(ind,a)
plt.barh(ind,b,left=a)
plt.barh(ind,c,left=a+b)

ind = np.array(range(0,len(moc_df)))
plt.bar(ind,moc_df["y"].values)
plt.bar(ind,moc_df["z"].values,bottom=moc_df["y"].values)

# +
print(plot.get_values_by_keys(["x","y","z"])({
    "y" : (0,1,2),
    "x" : [0,0,0],
}))

print(
    plot.to_flatlist(
        {
                "y" : ([0],1,2),
                "x" : [0,0,0],
        }
        
    )
)

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
# -


