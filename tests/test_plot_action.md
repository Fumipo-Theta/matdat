---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.2
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.7.0
---

```python
import matplotlib.pyplot as plt
import func_helper.func_helper.iterator as it
import func_helper.func_helper.dictionary as dictionary

import matdat.matdat.plot as plot
import pandas as pd
import numpy as np
import math
from func_helper import pip
from matdat import Figure, Subplot
```

## xyz sequential data

```python
"""
Moc of sequential data
"""

moc = dictionary.over_iterator(
    x=lambda x:x,
    y=lambda x:x*x,
    z=lambda x:np.sin(x*math.pi)
)(np.arange(-5,5,0.1))
```

## Test of plot actions


### Axes styling

```python
# Default style defining in Subplot class
I_default_style_plot = Subplot.create().add(
    data=moc,
    xlabel="x",
    ylabel="y",
)

I_custom_style_plot = I_default_style_plot.forked(
    label=dict(fontsize=20,color="red"),
    xlabel_setting=dict(color="blue"),
    tick=dict(labelsize=10),
    xtick=dict(color="blue"),
    xlim=[0,100],
    ylim=[-10,10]
)

I_single_plot = Subplot.create(label={"fontsize":16},tick={"labelsize":10}).add(
    data=moc,
    x="x",
    y="y",
    xlabel="x",
    ylabel="y",
)

I_multi_plot = I_single_plot.forked(dict(
    x="x",
    y=plot.multiple("y","z"),
))
```

```python
Figure.create().add_subplot(
    I_default_style_plot.set_title("Default style"),
    I_custom_style_plot.set_title("Custom style"),
).show(size=(4,4),margin=(1,1),column=2)
```

### Line plot

```python
Figure.create().add_subplot(
    I_single_plot.forked(dict(plot=[plot.line()])),
    I_multi_plot.forked(dict(plot=[plot.line()]))
).show(size=(5,5),margin=(1,1),column=2)
```

### Scatter plot

```python
Figure.create().add_subplot(
    I_single_plot.forked(dict(plot=[plot.scatter(s=lambda df:df["y"])])),
    I_multi_plot.forked(dict(plot=[plot.scatter()])),
    I_single_plot.forked(dict(plot=[plot.scatter(alpha=0.5),plot.line()])),
    I_multi_plot.forked(dict(plot=[plot.scatter(s=0.5),plot.line()]))
).show(size=(4,4),column=2)
```

### Vertical line plot

```python
Figure.create().add_subplot(
    I_single_plot.forked(dict(plot=[plot.vlines(lower=5, linestyle="--")])),
    I_multi_plot.forked(dict(plot=[plot.vlines(color=plot.multiple("C0","C1"))]))
).show(size=(5,5),margin=(1,1),column=2)
```

### Band plot

```python
Figure.create().add_subplot(
    I_single_plot.forked(dict(plot=[plot.scatter(),plot.yband(xpos=0.5,color="blue")])),
    I_multi_plot.forked(dict(plot=[plot.scatter(),plot.yband(xpos=plot.multiple([-2,2],[-4,-3]))])),
).show(size=(4,4),column=2)
```

### Plot fill between lines

```python
Figure.create().add_subplot(
    I_single_plot.forked(dict(plot=[plot.fill_between(y2=5)])),
    I_multi_plot.forked(dict(plot=[plot.fill_between(y2="z")])),
).show(size=(4,4),column=2)
```

## Discontinuous data

```python
moc_count = dictionary.over_iterator(
    normal = lambda x: np.random.normal(),
    xcount = lambda x: np.random.normal() + 0.5 * x*x,
    ycount = lambda x: np.random.normal(scale=0.5) +  x,
    x = lambda x: x,
    xdensity = lambda x: np.exp(-x*x/2)/np.sqrt(2*math.pi)
)(np.linspace(-5,5,1000))

I_hist_plot = Subplot.create().add(
    data = moc_count,
    y="normal",
    
)
```

### Histogram plot

```python
vertical_hist = I_hist_plot.forked(dict(plot=[plot.hist(bins=20,density=True)])).add(
        data=moc_count,
        x="x",
        y="xdensity",
        plot=[plot.line(color="k")],
    )

horizontal_hist = vertical_hist.forked(
    dict(orientation="horizontal"),
    dict(x="xdensity",y="x")
)

Figure.create().add_subplot(
    vertical_hist,
    horizontal_hist,
).show(size=(4,4),column=2)
```

### Joint plot

```python
def joint_plot(data,x,y,*,scatter=plot.scatter(),hist=plot.hist(),dpi=72):
    scatter_width = 5
    scatter_height = 5
    hist_height = 1
    hist_width = 1
    scatter_size = (scatter_width,scatter_height)
    x_hist_size = (scatter_width,hist_height)
    y_hist_size = (hist_width,scatter_height)
    empty_size = (hist_width,hist_height)
    
    ax_sizes = [x_hist_size,empty_size,scatter_size,y_hist_size]
    
    base_plot = Subplot.create(label={"fontsize":18})

    empty_space = Subplot.create_empty_space()

    scatter_plot = base_plot.forked().add(
        data=data,
        x=x,
        y=y,
        xlabel=x,
        ylabel=y,
        plot=[scatter]
    )
    
    x_hist = base_plot.forked(tick={"labelleft":False,"labelbottom":False}).add(
        data=moc_count,
        y=x,
        plot=[hist]
    )
    
    y_hist = base_plot.forked(tick={"labelleft":False,"labelbottom":False}).add(
        data=moc_count,
        y=y,
        orientation="horizontal",
        plot=[hist]
    )
    
    return Figure.create().add_subplot(
        x_hist,
        empty_space,
        scatter_plot,
        y_hist,
        name=[
            "x_hist",
            "empty",
            "scatter",
            "y_hist"
        ]
    ).show(size=ax_sizes,column=2,margin=(0,0),dpi=dpi)
    
joint_plot(moc_count,"xcount","ycount",scatter=plot.scatter(alpha=0.5),hist=plot.hist(density=True),dpi=72)
```

### Box plot

```python
Figure.create().add_subplot(
    Subplot.create().add(
        data=moc_count,
        y=["xcount","ycount"],
        plot=[plot.box()]
    ),
    Subplot.create().add(
        data=moc_count,
        y=["xcount","ycount"],
        plot=[plot.box(vert=False)]
    ),
).show(size=(6,6),column=2)
```

```python
pip(
    plot.line()(moc,{
        "x" : "x",
        "y" : ("y")
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
            "y":["y","z"],
            "ylim" : None
        }
    )
)(plt.subplot())
```

```python
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
```

```python
plot.box(showmeans=True,meanprops=({"marker":"o"}))(
    moc_df,
    y=["y","z"],
    vert=False
)(plt.subplot())
```

```python
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
        plot=[plot.line()]
    )
)

fig, axs = figure.show(size=(8,6))
```

```python
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
```
