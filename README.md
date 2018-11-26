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
from matdat import Figure, Subplot, SubplotTime
```

#### Subplot and SubplotTime

They are extended from abstruct base class ISubplot, which has public methods: `add` and `plot`.
SubplotTime is extended from Subplot.
You can use SubplotTime when reading external file of time series data.

Instance of these classes store:
    1. data source
    2. plot actions
    3. settings for plot actions
    4. the limit of axis range
    5. the style of axis labels and ticks

These instance draw plot on ax subplot of matplotlib by `plot` method.

```python
# plot action with styling is reusable.
scatter = plot_action.scatter(s=2,c="blue")

# subplot with data and plot actions is reusable
subplot = Subplot(title="subplot title",style={"title":{"fontsize":24}})\
.add(
    dataframe,
    plot=[plot_action.line(linewidth=1.5),scatter],
    x="x column name",
    y="y column name",
    xlim=[-10,10],
    label={"fontsize":20},
    xlabel="x",
    ylabel="y",
    tick={"labelsize":14},
    xtick={"rotation":45}
)\
.add(
    data_file_path,
    dataInfo={"header":0},
    plot=[scatter],
    x="x column name",
    y="y column name"
)

ax = subplot.plot(matplotlib.pyplot.subplot())
```

Subplot and SubplotTime can use dictionary, pandas.DataFrame, and path to csv and excel files as data source.
The data is transformed into pandas.DataFrame internaly.
The additional dict parameter "dataInfo" is needed when you set path to files.
The keys and values of the dict must be compatible parameter for read method of pandas such as `pandas.read_csv`.

When path to csv files are set, the file is read and hold just when `plot` method is called.

The setting parameters for plot action define the name of columns used in plotting, range of axis, and label of axis.

The parameter plot is list of plot actions.


#### Figure

Figure stores ISubplot instances.
When `show` method is called,
matplotlib.axes._subplots.AxesSubplot is created,
then Isubplot instances read data and plots on axes.

In `show` method, subgrids formed by matpos package can be used to define layout.

The most simple plot is `show` method with the same size subplots.

```python
fig = Figure()

fig.add_subplot(sub_a, "a")
fig.add_subplot(sub_b, "b")
fig.add_subplot(sub_c)
fig.add_subplot(sub_d)

padding = {
    "top" : 0.5,
    "left" : 1,
    "bottom" : 1,
    "right" : 0.5
}

figure, axs = fig.show(size=(8,6), column=2, margin=(1,0.5), padding=padding)
```

The list of sizes can be used for grid layout with different size subplots.

```python
sizes = [(8,6), (4,6), (8,6), (4,6)]

figure, axs = fig.show(size=sizes, column=2, margin=(1,0.5),padding=padding)
```

You can also use dictionary defining parameters in show().

```python
setting = {
    "size" : [(400,300), (400,300), (300,300), (300,300)],
    "column" : 2,
    "margin" : (50,25),
    "padding" : {"left":50,"bottom":25,"top":25,"right":25},
    "unit" : "px",
    "dpi" : 100
}

figure, axs = fig.show(setting)
```

And more, you can make complex layout by using subgrids by Matpos.

```python
mp = MatPos(unit="cm")

a = mp.from_left_top(mp,(12,8))
b = mp.add_right(a, (8,8), margin=1)
c = mp.add_bottom(a, (12,6), margin=0.5)
d = mp.add_bottom(d, (12,6), margin=0.5)

figure, axs = fig.show(mp,[a,b,c,d],padding=padding)
```

The axs is dictionary of Axsubplot

```python
axs = {
   "a" : matplotlib.axes._subplot.Axsubplot,
   "b" : matplotlib.axes._subplot.Axsubplot,
   3 : matplotlib.axes._subplot.Axsubplot,
   4 : matplotlib.axes._subplot.Axsubplot,
 }
```

Therefore, you can access each subplot by using this object.