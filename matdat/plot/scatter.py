from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, get_literal_or_series
from .action import DataSource, AxPlot


def _scatter_plotter(df: DataSource, x, y, *arg, c=None, s=None, marker=None, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    colors = get_literal_or_series(c,df)
    sizes = get_literal_or_series(s,df)

    def plot(ax):
        ax.scatter(_x, _y, s=sizes, c=colors, **kwargs)
        return ax
    return plot


def scatter(**presetting):
    return plot_action(
        _scatter_plotter,
        ["x", "y"],
        {**default_kwargs.get("scatter")}
    )(**presetting)
