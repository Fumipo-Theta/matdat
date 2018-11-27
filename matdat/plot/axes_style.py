from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset
from .action import DataSource, AxPlot
from typing import Optional
import numpy as np


def set_cycler(cycler=None):
    def setter(ax):
        if cycler is 'default':
            return ax
        elif cycler is None:
            return ax
        else:
            ax.set_prop_cycle(cycler)
        return ax
    return setter


def _get_lim(df: DataSource, lim_list: Optional[list]):
    try:
        if lim_list is not None and len(lim_list) >= 2:
            lim = [*lim_list]
            if lim[0] is None:
                lim[0] = np.min(df.min())
            if lim[1] is None:
                lim[1] = np.max(df.max())
            return lim
        else:
            return [
                np.min(df.min()),
                np.max(df.max())
            ]
    except:
        print(f"Failed: Set limit {lim_list}.")
        return None


def _get_lim_parameter(df: DataSource, lim_list: Optional[list]):
    if lim_list is not None and len(lim_list) >= 2:
        return lim_list
    else:
        return None


def _xlim_setter(df: DataSource, x, *arg, xlim=None, **kwargs)->AxPlot:
    """
    Parameters
    ----------
    x
    """
    lim = _get_lim_parameter(get_subset()(df, x), xlim)

    def plot(ax):
        if lim is not None:
            now_lim = ax.get_xlim()
            next_lim = [None, None]
            next_lim[0] = lim[0] if lim[0] is not None else now_lim[0]
            next_lim[1] = lim[1] if lim[1] is not None else now_lim[1]
            ax.set_xlim(next_lim)
        return ax
    return plot


def _ylim_setter(df: DataSource, y, *arg, ylim=None, **kwargs)->AxPlot:
    """
    Parameters
    ----------
    y
    """
    lim = _get_lim_parameter(get_subset()(df, y), ylim)

    def plot(ax):
        if lim is not None:
            now_lim = ax.get_ylim()
            next_lim = [None, None]
            next_lim[0] = lim[0] if lim[0] is not None else now_lim[0]
            next_lim[1] = lim[1] if lim[1] is not None else now_lim[1]
            ax.set_ylim(next_lim)
        return ax
    return plot


def set_xlim(**presetting):
    """
    Set xlim of ax.

    xlim is list of numbers.
    """
    return plot_action(
        _xlim_setter,
        generate_arg_and_kwags(get_value()),
        ["x"],
        {"xlim": None},
    )(**presetting)


def set_ylim(**presetting):
    return plot_action(
        _ylim_setter,
        generate_arg_and_kwags(get_value()),
        ["y"],
        {"ylim": None},
    )(**presetting)


def _grid_setter(*arg, **kwargs)->AxPlot:
    def plot(ax):
        ax.grid(**kwargs)
        return ax
    return plot


def set_grid(**presetting):
    return plot_action(
        _grid_setter,
        generate_arg_and_kwags(get_value()),
        [],
        default_kwargs.get("grid")
    )(**presetting)


def _tick_params_setter(df, axis, *arg, **kwargs)->AxPlot:
    def plot(ax):
        if axis is "both":
            ax.tick_params(axis=axis, **kwargs)
        else:
            ax.tick_params(
                axis=axis, **dict(filter(lambda kv: kv[0] in default_kwargs.get("tick_params_each"), kwargs.items())))
        return ax
    return plot


def set_tick_parameters(**presetting):
    return plot_action(
        _tick_params_setter,
        generate_arg_and_kwags(get_value()),
        ["axis"],
        default_kwargs.get("tick_params")
    )(**presetting)


def _axis_scale(*arg, xscale=None, yscale=None):
    def plot(ax):
        if xscale is not None:
            ax.set_xscale(xscale)
        if yscale is not None:
            ax.set_yscale(yscale)
        return ax
    return plot


def axis_scale(**presetting):
    return plot_action(
        _axis_scale,
        generate_arg_and_kwags(get_value()),
        [],
        {"xscale": None, "yscale": None}
    )(**presetting)


def _label_setter(df: DataSource, xlabel: str, ylabel: str, *arg, **kwargs)->AxPlot:
    def plot(ax):
        if xlabel is not None:
            ax.set_xlabel(
                xlabel,
                **kwargs
            )
        if ylabel is not None:
            ax.set_ylabel(
                ylabel,
                **kwargs
            )
        return ax
    return plot


def set_label(**presetting):
    return plot_action(
        _label_setter,
        generate_arg_and_kwags(get_value("")),
        ["xlabel", "ylabel"],
        default_kwargs.get("axis_label")
    )(**presetting)
