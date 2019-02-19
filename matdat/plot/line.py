from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, get_literal_or_series
from .action import DataSource, AxPlot, Selector


@plot_action(["x", "y"],
             default_kwargs.get("line"))
def line(
        df: DataSource, x: Selector, y: Selector,
        *arg,
        color=None,
        **kwargs)->AxPlot:

    if len(df) is 0:
        return lambda ax: ax

    _x = get_subset()(df, x)
    _y = get_subset()(df, y)
    _color = get_literal_or_series(color, df)

    def plot(ax):
        ax.plot(_x, _y, color=_color, **kwargs)
        return ax
    return plot
