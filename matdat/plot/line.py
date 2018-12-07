from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset
from .action import DataSource, AxPlot, Selector


def _line_plotter(df: DataSource, x: Selector, y: Selector, *arg, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    def plot(ax):
        ax.plot(_x, _y, **kwargs)
        return ax
    return plot


def line(**presetting):
    return plot_action(
        _line_plotter,
        ["data", "x", "y"],
        default_kwargs.get("line")
    )(**presetting)
