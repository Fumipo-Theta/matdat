from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset
from .action import DataSource, AxPlot


def _scatter_plotter(df: DataSource, x, y, *arg, s_name=None, c_name=None, **kwargs)->AxPlot:
    if c_name is not None:
        kwargs.update({"c": get_subset(False)(df, c_name)})
    if s_name is not None:
        kwargs.update({"s": get_subset(False)(df, s_name)})
    _x = get_subset()(df, x)
    _y = get_subset()(df, y)

    def plot(ax):
        ax.scatter(_x, _y, **kwargs)
        return ax
    return plot


def scatter(**presetting):
    return plot_action(
        _scatter_plotter,
        generate_arg_and_kwags(get_value()),
        ["x", "y"],
        {**default_kwargs.get("scatter"), "c_name": None, "s_name": None}
    )(**presetting)
