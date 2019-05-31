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
import numpy as np

import matdat.matdat.plot as plot
from matdat.matdat.plot.action import plot_action, selector_or_literal, get_subset
from matdat import Figure, Subplot
import func_helper.func_helper.dictionary as dictionary

import matplotlib.pyplot as plt
```

```python
moc = dictionary.over_iterator({
    "x" : lambda i: np.sin(i * 2) + np.sin(i * 5),
    "y" : lambda i: np.cos(i * 2) + np.cos(i * 5),
    "i" : lambda i: i
})(np.arange(0,10,0.1))

fig, axes = Figure().add_subplot(
    Subplot().add(
        data=moc,
        x="i",
        y=plot.multiple("x","y"),
        plot=[plot.line()]
    )
).show(size=(8,4))

axes[1].legend(["x","y"])

```

rose diagram

密度分布を極座標にマッピングする.

* direction
* density: frequency * weight

# ```python
def rose(df, direction, frequency, weight, *, bins=36):
    def apply(ax):
        pass
    return apply
# ```

```python
@plot_action(["vector"])
def rose(
    df,
    vector,
    section_width
)
```
