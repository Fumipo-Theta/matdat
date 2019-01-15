from .i_plot_size import IPlotSize


class A4Portrait(IPlotSize):
    def __init__(
        self,
        row: int=1,
        column: int=1,
        margin=(1, 1),
        padding={},
        figsize=(8.27*2, 11.69*2),
        dpi: int=144,
        **kwargs
    ):
        self.row = row
        self.column = column
        self.margin = margin
        self.padding = {
            "left": 1,
            "right": 0.5,
            "top": 1,
            "bottom": 1,
            **padding
        }
        self.figsize = figsize
        self.dpi = dpi
        self.kwargs = kwargs

    def __new__(cls, *arg, **kwargs):
        return super().__new__(cls)

    def make_grid(self):
        return [(5, 5)] * (self.row*self.column)

    def use(self)->dict:
        return {
            "size": self.make_grid(),
            "column": self.column,
            "margin": self.margin,
            "padding": self.padding,
            "figsize": self.figsize,
            "dpi": self.dpi,
            **self.kwargs
        }
