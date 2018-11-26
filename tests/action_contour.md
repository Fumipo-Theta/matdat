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
from matdat import Figure, Subplot
import matdat.matdat.plot as plot
from matdat.matdat.plot import plot_action, generate_arg_and_kwags, get_value, get_subset
from matpos import Matpos
from func_helper import pip
```

```python
import pandas as pd
moc = pd.DataFrame({
    "x" : range(0,21),
    "y" : [(x-10)*(x-10) for x in range(0,21)],
    "z" : [(x-10) for x in range(0,21)]
})
moc.head()
```

```python
figure = Figure()

"""
set_titleのfontfamilyがうまく変更されない?
日本語を表示するには日本語対応のttcフォントを指定する必要があるが, 日本語もasciiも
全てそのフォントで表示されてしまう.
"""

figure.add_subplot(
    Subplot.create(style={"title":{"fontsize":20,"fontdict":{"family":["serif"]}}},title="(a)")\
    .add(
        moc,
        x="x",
        label = {"family":["serif"],"fontstyle":"italic","color":"blue"},
        xlabel="x 日本語",
        ylabel=r"$f(x) \frac{\infty}{b}$",
        y=("y","z"),
        plot=[plot.scatter()]
    )

)

figure.add_subplot(
    Subplot.create(title="(b)")\
    .add(
        moc,
        x="x",
        xlabel="日本語",
        xlim=[0,10],
        plot=[plot.scatter(y="y",c="red"),plot.scatter(y="z")]
    )\
)

fig, axs = figure.show(size=(400,400),column = 2,margin=50,padding={"left":100},unit="px",dpi=100)
axs[1].legend(["${(x-10)}^2$","$x-10$"])
fig?
```

```python
figure = Figure()

figure.add_subplot(
    Subplot.create()\
    .add(
        moc,
        x="x",
        plot=[plot.scatter(y="y"),plot.scatter(y="z")]
    )
)

mp = Matpos(unit="px",dpi=100)
a = mp.add_right(mp,size=(600,400))
figure.show(mp,[a])
```

```python
import matplotlib.pyplot as plt
```

```python

```

```python
ax = plt.subplot()
ax.set_title("x",fontsize=20,fontstyle="normal",family=["serif"])
```

## contour

```python
import numpy as np

# [matplotlib.pyplot.contour — Matplotlib 3.0.2 documentation](https://matplotlib.org/api/_as_gen/matplotlib.pyplot.contour.html)

def _contour(df, x, y, z, **kwargs):
    X,Y = np.meshgrid(
        get_subset()(df,x),
        get_subset()(df,y)
    )
    Z = z(X,Y) if callable(z) else z
    def plot(ax):
        ax.contour(X,Y,Z)
        return ax
    return plot

def contour(**presetting):
    return plot_action(
        _contour,
        generate_arg_and_kwags(get_value()),
        ["x", "y", "z"],
        {
        }
    )(**presetting)
    
```

```python
figure = Figure()

dat = {
    "x" : np.arange(-3,3,0.1),
    "y" : np.arange(-3,3,0.1)
}

figure.add_subplot(
    Subplot.create()\
    .add(
        dat,
        x="x",
        y="y",
        z = lambda x,y: np.exp(-x**2 - y**2),
        plot=[contour()]
    )
)

figure.show(size=(6,6))
```

```python

```
