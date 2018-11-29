from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset, selector_or_literal, Icoordinate_transform
from .action import DataSource, AxPlot


def _text_plotter(df: DataSource, x, y, text, *arg,
                  xcoordinate=None,
                  ycoordinate=None,
                  **kwargs):
    _x = selector_or_literal(df, x)
    _y = selector_or_literal(df, y)
    _text = selector_or_literal(df, text)

    def plot(ax):
        for x, y, t in zip(_x, _y, _text):
            transform = Icoordinate_transform(ax, xcoordinate, ycoordinate)
            ax.text(x, y, t, transform=transform, **kwargs)
        return ax
    return plot


def text(**presetting):
    return plot_action(
        _text_plotter,
        ["x", "y", "text"],
        default_kwargs.get("text")
    )(**presetting)
