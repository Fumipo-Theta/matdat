from .action import default_kwargs, plot_action, generate_arg_and_kwags, get_value, get_subset
from .action import DataSource, AxPlot, Selector
import matplotlib.image as mpimg


@plot_action(
    ["img_like"],
    {
        "cmap": None,
    }
)
def imshow(df, img_like, *arg, **kwargs)->AxPlot:
    """
    Parameters
    ----------
    df: image like data
        Such as numpy array.

    """
    img = mpimg.imread(img_like)

    def plot(ax):
        ax.imshow(img)
        return ax
    return plot
