from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, Iget_factor
from .action import DataSource, AxPlot


def _fill_between_plotter(data, x, y, y2=0, cmap=None, **kwargs)->AxPlot:
    if len(data) is 0:
        return lambda ax: ax

    _x = get_subset()(data, x)
    _y = get_subset()(data, y)
    _y2 = get_subset()(data, y2)

    print(kwargs)

    def plot(ax):
        ax.fill_between(_x, _y, _y2, **kwargs)
        return ax

    return plot


def fill_between(**presetting):
    return plot_action(
        _fill_between_plotter,
        ["x", "y"],
        {
            "y2": 0,
            **default_kwargs.get("fill"),
            "color": "blue"
        }
    )(**presetting)
