from .i_plot_size import IPlotSize


class Slide4x3(IPlotSize):
    def __init__(
        self,
        row: int=1,
        column: int=1,
        margin=(1, 1),
        padding={},
        figsize=(10, 7.5),
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


class Slide16x9(IPlotSize):
    def __init__(
        self,
        row: int=1,
        column: int=1,
        margin=(1, 1),
        padding={},
        figsize=(16 * 7.5/9, 7.5),
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
