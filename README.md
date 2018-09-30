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
the data is transformed to pandas.DataFrame internaly.
The additional parameter "dataInfo" is needed when you set path to csv files, in which index of header row and column names used as time series index.

When path to csv files are set, the file is not read immidiately.

The parameter "option" defines the name of columns used in plotting, range of axis, and label of axis.

The parameter plot defines the way to plot the data,


```python
sub_a = Subplot(ax_style)
sub_a.register(
    data_like,
    dataInfo,
    option,
    plotActions = [linePlot({"lineColor": "red})],
    limit,
    transform
)

sub_b.register(
    {"x": list_x, "y": list_y},
    option={
        "x": "x",
        "y": y"
    },
    plot=[limit_position]
)

sub_c = Subplot()
    .c{
        dataframe,

    }
```

Point free style:

```python
sub_a = SubplotTime.create(ax_style)\
    .register()
```

#### Figure

Figure stores Subplot or SubplotTime, and trigger plotting.
When `show()`, `show_grid()`, or `show_custom()` method is called,
matplotlib.pyplot.axsubplot is created,
data is read,
and the data is plotted on ax.
In the plotting, subgrids formed by matpos package can be used to define layout.

```python
fig = Figure(figureStyle={"column":2}, padding)

fig.add_subplot(sub_a, "a")
fig.add_subplot(sub_b, "b")
fig.add_subplot(sub_c, "c")
fig.add_subplot(sub_d, "d")

axes = fig.show()
```

```python
axes = fig.show_grid([(8,6) for i in range(fig.get_length())], column=2, distance=(1,0.5))
```