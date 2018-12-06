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
import pandas as pd
import numpy as np
from matdat import Figure, Subplot, SubplotTime
import matdat.matdat.plot as plot
import func_helper.func_helper.dataframe as dataframe
import func_helper.func_helper.dictionary as dictionary
from func_helper import pip,identity
```

```python
moc = pip(
    dictionary.over_iterator({
        "date" : lambda i: f"2018/12/{1+i}",
        "y" : lambda x: x * x 
    }),
    pd.DataFrame,
)(range(20))

moc_time_idx = pip(
    dictionary.over_iterator({
        "date" : lambda i: f"2018/12/{1+i}",
        "y" : lambda x: x * x 
    }),
    pd.DataFrame,
    dataframe.setTimeSeriesIndex(["date"])
)(range(20))


print(moc.dtypes)
display(moc.head())

print(moc_time_idx.dtypes)
display(moc_time_idx.head())
print(moc_time_idx.index)
```

```python
dataframe.filter_between(
    *pd.to_datetime([None,"2018/12/10"])
)(moc_time_idx)
```

```python
dataframe.filter_between(
    *pd.to_datetime(["2018/12/5","2018/12/10"])
)(moc_time_idx)
```

```python
figure = Figure()

IbySubplot = Subplot.create(xFmt="%y/%m/%d").add(
    y="y",
    plot=[plot.line(),plot.scatter()]
)

subplot_time_idx=IbySubplot.tee(dict(
    data = moc_time_idx,
    xlim = pd.to_datetime(["2018/12/5"])
))

subplot_transform = IbySubplot.tee(dict(
    data = moc,
    transform = dataframe.setTimeSeriesIndex(["date"]),
    xlim = pd.to_datetime(["2018/12/5","2018/12/10"]),
    #xlim = ["2018/12/5","2018/12/10"],
))


figure.add_subplot(subplot_time_idx)
figure.add_subplot(subplot_transform)
figure.add_subplot(subplot_transform.tee(dict(xlim=["2018/12/5"])))
figure.show(size=(8,4))
```

```python
figure = Figure()

IbySubplotTime = SubplotTime.create(xFmt="%m/%d").add(
    y="y",
    plot=[plot.line(),plot.scatter()]
)

# indexがpandas.datetimeのとき
time_subplot = IbySubplotTime.tee(dict(
    data=moc_time_idx,
    xlim=["2018/12/5","2018/12/10"]
))

# indexがpandas.datetimeでないとき, indexオプションを指定. 
time_subplot_index=IbySubplotTime.tee(dict(
    data = moc,
    index=["date"],
    xlim=["2018/12/5",None],
))

# Subplotでもdatetimeをプロット可能. 軸目盛りのフォーマットはデフォルトのままとなる.
subplot_index = IbySubplot.tee(dict(
    data = moc,
    #index=["date"],
    xlim=["2018/12/5",None],
))

figure.add_subplot(time_subplot)
figure.add_subplot(time_subplot_index)
figure.add_subplot(time_subplot_index.tee(dict(xlim=[None,"2018/12/10"])))
figure.add_subplot(subplot_index)
figure.add_subplot(subplot_index.tee(dict(xlim=pd.to_datetime(["2018/12/5",None]))))
figure.show(size=(8,4))
```

```python
time_subplot.axes_style
```

```python

```
