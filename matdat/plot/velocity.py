from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset
from .action import DataSource, AxPlot


@plot_action(["x", "ex", "ey"],
             {**default_kwargs.get("quiver"),
              "scale": 1,
              "scale_units": "y",
              "alpha": 0.3,
              "color": "gray",
              "width": 0.001,
              "headwidth": 5,
              "headlength": 10
              })
def velocity(df: DataSource, x, ex, ey, *arg, **kwargs)->AxPlot:
    _x = get_subset()(df, x)
    _y = [0. for i in _x],
    _ex = get_subset()(df, ex)
    _ey = get_subset()(df, ey)

    def plot(ax):
        ax.quiver(_x, _y, _ex, _ey, **kwargs)
        return ax
    return plot
