# matdat

Providing layer of data and plot methods separating from layout for matplotlib.
matdat.Figure store information of Subplot and finally, intagrate the subplots.
matdat.Subplot and matdat.SubplotEime provide lazy data reading and ploting.
The Subplot instances store the way to read data and the way to plot data.
Therefore, data is not read on memory and drawing is not run until method of plotting has called.

## Usage

### Install

By pip,

```
pip install git+https://github.com/Fumipo-Theta/matdat.git
```

### Import

```python
from matdat import Figure, Subplot, Subplottime
```

#### Subplot and SubplotTime

Instance of these classes store:
    1. data for plot or the way to read data
    2. plot option
    3. option in plot
    4. the way to plot
    5. the limit of axis range

Subplot and SubplotTime can use dictionary, pandas.DataFrame, and path to csv files
    as data source.
The data is transformed to pandas.DataFrame internaly.
The additional parameter "dataInfo" is needed when you set path to csv files, in which index of header row and column names used as time series index.

When path to csv files are set, the file is not read immidiately.

The parameter "option" defines the name of columns used in plotting, range of axis, and label of axis.

The parameter plot defines the way to plot the data,


```python
ax_style = {
    "label_size" : 20,
    "tick_size" : 14
}

sub_a = Subplot(ax_style)
sub_a.register(
    paths_to_csv_files,
    dataInfo = {
        "header" : 5
    },
    option = {
        "x" : "column_of_x",
        "xlim" : [-100, 100],
        "xlabel" : "X axis",
        "y" : "column_of_y",
        "ylim" : [0, 100],
        "ylabel" : "Y axis"
    },
    plotActions = [
        linePlot({"lineColor": "red"}),
        scatterPlot(),
        showGrid("both")
    ],
    transform = lambda d: d["column_of_y"] = 0 if d["confidence"] < 0.05 else d["column_of_y"]
)

sub_b = Subplot(ax_style)
sub_b.register(
    {"x": list_x, "y": list_y},
    option={
        "x": "x",
        "y": "y"
    },
    plot=[linePlot()]
)
sub_b.register(
    dataframe,
    option={
        "x" : "column_x",
        "y" : "column_y"
    },
    plot=[scatterPlot()]
)

```

Point free style:

```python
sub_a = SubplotTime.create(ax_style)\
    .register()\
    .register()
```

#### Figure

Figure stores Subplot or SubplotTime, and trigger plotting.
When `show()` method is called,
matplotlib.axes._subplots.AxesSubplot is created,
then data is read,
and finally the data is plotted on axes.

The data source can be dictionaly containing lists, pandas.DataFrame, and list of path to csv files.
All data type converted to pands.DataFrame internally.

In plotting, subgrids formed by matpos package can be used to define layout.

The most simple plot is `show` method with the same size subplots.

```python
fig = Figure()

fig.add_subplot(sub_a, "a")
fig.add_subplot(sub_b, "b")
fig.add_subplot(sub_c)
fig.add_subplot(sub_d)

axs = fig.show((8,6), column=2, margin=(1,0.5), padding=padding)
```

The list of sizes can be used for grid layout with different size subplots.

```python
sizes = [(8,6), (4,6), (8,6), (4,6)]

axs = fig.show(sizes, column=2, margin=(1,0.5),padding=padding)
```

And more, you can make complex layout by using subgrids by MatPos.

```python
mp = MatPos()

a = mp.from_left_top(mp,(4,3))
b = mp.add_right(a, (2,2), margin=1)
c = mp.add_bottom(a, (4,1), margin=0.5)
d = mp.add_bottom(d, (4,1), margin=0.5)

axs = fig.show(mp,[a,b,c,d],padding=padding)
```

The axs is dictionary of Axsubplot

```python
axs = {
   "a" : matplotlib.axes._subplot.Axsubplot,
   "b" : matplotlib.axes._subplot.Axsubplot,
   2 : matplotlib.axes._subplot.Axsubplot,
   3 : matplotlib.axes._subplot.Axsubplot,
 }
```

Therefore, you can access each subplot by using this object.