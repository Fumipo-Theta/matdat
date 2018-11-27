from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, Icoordinate_transform
from .action import DataSource, AxPlot
import numpy as np
import pandas as pd


def _xband_plotter(df: DataSource, x, y, *arg, xlim=None, ypos=None, **kwargs)->AxPlot:

    def plot(ax):
        if ypos is None:
            return ax

        if type(ypos) not in [
            list, tuple, np.ndarray,
            pd.core.indexes.datetimes.DatetimeIndex,
            pd.core.series.Series
        ]:

            _kwargs = dict(
                filter(lambda kv: kv[0] in default_kwargs.get(
                    "axline"), kwargs.items())
            )
            ax.axhline(ypos, **_kwargs)

        elif len(ypos) <= 0:
            print("ypos must be list like object with having length >= 1.")

        else:
            ax.fill(
                [0, 1, 1, 0],
                [ypos[0], ypos[0], ypos[1], ypos[1]],
                transform=Icoordinate_transform(ax, "axes", "data"),
                **kwargs
            )
        return ax
    return plot


def _yband_plotter(df: DataSource, x, y, *arg, ylim=None, xpos=None, **kwargs)->AxPlot:

    def plot(ax):

        if xpos is None:
            return ax

        if type(xpos) not in [
            list, tuple, np.ndarray,
            pd.core.indexes.datetimes.DatetimeIndex,
            pd.core.series.Series
        ]:

            _kwargs = dict(
                filter(lambda kv: kv[0] in default_kwargs.get(
                    "axline"), kwargs.items())
            )
            ax.axvline(xpos, **_kwargs)

        elif len(xpos) <= 0:
            print("xpos must be list like object with having length >= 1.")

        else:

            ax.fill(
                [xpos[0], xpos[0], xpos[1], xpos[1]],
                [0, 1, 1, 0],
                transform=Icoordinate_transform(ax, "data", "axes"),
                **kwargs
            )
        return ax
    return plot


def xband(**presetting):
    return plot_action(
        _xband_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**default_kwargs.get("fill"), "xlim": None, "ypos": None}
    )(**presetting)


def yband(**presetting):
    return plot_action(
        _yband_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**default_kwargs.get("fill"), "ylim": None, "xpos": None}
    )(**presetting)
