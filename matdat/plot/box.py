from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, Iget_factor
from .action import DataSource, AxPlot
from typing import Union, List
import pandas as pd


def _box_plotter(df: DataSource, ys: Union[str, List[str]], *arg, **kwargs)->AxPlot:
    """
    Generate box plots for indicated columns.
    """
    _ys = ys if type(ys) is list else [ys]

    def plot(ax):
        ax.boxplot(
            [df[y].dropna() for y in _ys],
            labels=_ys,
            positions=range(0, len(_ys)),
            **kwargs
        )
        return ax
    return plot


def box(**presetting):
    return plot_action(
        _box_plotter,
        generate_arg_and_kwags(get_value()),
        ["y"],
        default_kwargs.get("box")
    )(**presetting)


def _factor_box_plotter(df: DataSource, x, y, *arg, xfactor=None, **kwargs)->AxPlot:
    """
    Generate box plots grouped by a factor column in DataFrame.

    """
    _factor_series, _factor = Iget_factor(df, x, xfactor)
    _factor_detector = pd.Categorical(
        _factor_series, ordered=True, categories=_factor)

    _group = df.groupby(_factor_detector)
    _data_without_nan = [df.loc[_group.groups[fname]][y].dropna()
                         for fname in _factor]

    def plot(ax):
        if len(_data_without_nan) is 0:
            print("No data for box plot")
            return ax
        ax.boxplot(
            _data_without_nan,
            labels=_factor,
            positions=range(0, len(_factor)),
            **kwargs
        )

        if kwargs.get("vert", True):
            ax.set_xticks(list(range(0, len(_factor))))
            ax.set_xticklabels(_factor)
            ax.set_xlim([-1, len(_factor)])
        else:
            ax.set_yticks(list(range(0, len(_factor))))
            ax.set_yticklabels(_factor)
            ax.set_ylim([-1, len(_factor)])
        return ax
    return plot


def factor_box(**presetting):
    return plot_action(
        _factor_box_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**default_kwargs.get("box"), "xfactor": None}
    )(**presetting)
