from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, get_literal_or_series
from .action import DataSource, AxPlot, SetData, Selector, LiteralOrSequencer


@plot_action(["x", "y"],
             {**default_kwargs.get("scatter")})
def scatter(
    data: DataSource,
    x: Selector,
    y: Selector,
    *arg,
    c: LiteralOrSequencer=None,
    s: LiteralOrSequencer=None,
    marker=None,
    **kwargs
)->AxPlot:

    if len(data) is 0:
        return lambda ax: ax

    _x = get_subset()(data, x)
    _y = get_subset()(data, y)

    colors = get_literal_or_series(c, data)
    sizes = get_literal_or_series(s, data)

    def plot(ax):
        ax.scatter(_x, _y, s=sizes, c=colors, **kwargs)
        return ax
    return plot
