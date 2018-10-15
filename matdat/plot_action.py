"""
plot actions  are function:

(setting_and_styles: any) -> (df: pandas.DataFrame, option_for_plot: dict)
    -> ax: matplotlib.pyplot._subplot.Axsubplot -> ax: matplotlib.pyplot._subplot.Axsubplot
"""

import numpy as np


_theme = {
    "plot_color": "#0078D7",
    "accent_color": "",
    "info_color": "green"
}

_default = {
    "line": {
        "linewidth": 1,
        "color": _theme["plot_color"],
        "alpha": 1.
    },
    "scatter": {
        "s": 2,
        "color": _theme["plot_color"],
        "alpha": 1.
    },
    "rect": {
        "color": _theme["info_color"],
        "alpha": 0.5
    },
    "arrow": {
        "alpha": 0.3,
        "color": "gray",
        "width": 0.001,
        "headwidth": 5,
        "headlength": 10
    },
    "string": {
        "label_size": 16,
        "tick_size": 10
    }
}

line_kwargs = [
    "color",
    "linestyle",
    "linewidth",
    "alpha"
]

scatter_kwargs = {
    "color",
    "s",
    "alpha",
    "marker",
    "edgecolors",
    "linewidth",
    "linestyle"
}


def setStyle(opt, style):
    def f(ax):
        ax.tick_params(axis="y", labelsize=style.get(
            "tick_size", _default["string"]["tick_size"]))
        ax.tick_params(axis="x", labelsize=style.get(
            "tick_size", _default["string"]["tick_size"]))

        if "xlabel" in opt:
            ax.set_xlabel(
                opt["xlabel"],
                fontsize=style.get(
                    "label_size", _default["string"]["label_size"])
            )

        if "ylabel" in opt:
            ax.set_ylabel(
                opt["ylabel"],
                fontsize=style.get(
                    "label_size", _default["string"]["label_size"])
            )

        return ax
    return f


def set_xlim(df, opt):
    def plot(ax):
        if len(df) == 0:
            return ax
        col = df[opt["x"]] if "x" in opt else df.index
        if (("xlim" in opt) and (len(opt["xlim"]) >= 2)):
            xlim = []
            _xlim = opt["xlim"]
            xlim.append(_xlim[0]
                        if _xlim[0] != None
                        else np.min(col))
            xlim.append(_xlim[1]
                        if _xlim[1] != None
                        else np.max(col))
            ax.set_xlim(xlim)
        else:
            ax.set_xlim([
                np.min(col),
                np.max(col)
            ])
        return ax
    return plot


def set_ylim(df, opt):

    def plot(ax):
        if len(df) == 0:
            return ax

        yName = opt.get("y")

        if (("ylim" in opt) and (len(opt["ylim"]) > 1)):
            ylim = opt.get("ylim")

            ylim[0] = ylim[0] if ylim[0] != None else df[yName].min()
            ylim[1] = ylim[1] if ylim[1] != None else df[yName].max()

            ax.set_ylim([ylim[0], ylim[1]])
        else:
            ax.set_ylim([
                df[yName].min(),
                df[yName].max()
            ])
        return ax
    return plot


def setGrid(axis="both", style={}):
    st = {
        "color": 'gray',
        "linestyle": ':',
        "linewidth": 1,
        **style
    }

    def setData(d, opt):
        def plot(ax):
            ax.grid(
                **st,
                axis=axis
            )
            return ax
        return plot
    return setData


def set_ylabel(name):

    def setData(d, opt):
        def plot(ax):
            ax.set_ylabel(name)
            return ax
        return plot
    return setData


def linePlot(style={}):

    def setData(df, opt):
        st = {
            k: v for k, v in
            filter(
                lambda kv: kv[0] in line_kwargs,
                {**_default["line"], **style, **opt.get("style", {})}.items())
        }

        def plot(ax):
            x = df[opt["x"]] if "x" in opt else df.index
            if (df[opt["y"]].dtype not in ["float64", "int64"]):
                return ax
            if (len(df) > 1):
                ax.plot(
                    x, df[opt["y"]],
                    **st
                )
            elif (len(df) == 0):
                ax = scatterPlot(st)(df, opt)(ax)
            else:
                None

            return ax
        return plot
    return setData


def scatterPlot(style={}):
    def setData(df, opt):
        st = {
            k: v for k, v in
            filter(
                lambda kv: kv[0] in scatter_kwargs,
                {**_default["scatter"], **style, **opt.get("style", {})}.items())
        }

        def plot(ax):
            x = df[opt["x"]] if "x" in opt else df.index

            if (df[opt["y"]].dtype not in ["float64", "int64"]):
                return ax
            if (len(df) > 0):
                ax.scatter(
                    x, df[opt["y"]],
                    **st
                )

            return ax
        return plot
    return setData


def movalMeanPlot(num=5, style={}):
    def setData(df, opt):
        def plot(ax):
            x = df[opt["x"]] if "x" in opt else df.index
            # num: 移動平均の個数
            b = np.ones(num)/num
            try:
                y2 = np.convolve(df[opt["y"]], b, mode='same')  # 移動平均

                ax.plot(x, y2, c="black", ls='--',
                        label='Moval mean '+str(num))
            except:
                return ax
            return ax
        return plot
    return setData


def barPlot(lower=0, style={}):
    def setData(df, opt):
        st = {
            k: v for k, v in
            filter(
                lambda kv: kv[0] in line_kwargs,
                {**_default["line"], **style, **opt.get("style", {})}.items())
        }

        def plot(ax):
            x = df[opt["x"]] if "x" in opt else df.index
            ax.vlines(
                x, [lower for i in x], df[opt["y"]],
                **st
            )
            return ax
        return plot
    return setData


def vLinePlotRGB(lower=0, style={}):
    def setData(df, opt):
        st = {**_default["line"], **style, **opt.get("style", {})}

        def plot(ax):
            x = df[opt["x"]] if "x" in opt else df.index
            ax.vlines(
                x, [lower for i in x], df[opt["y"]]+lower,
                color=df["rgb"],
                alpha=st["alpha"]
            )
            return ax
        return plot
    return setData


def bandPlot(xPos, style={}):
    def setData(df, opt):
        st = {
            k: v for k, v in
            filter(
                lambda kv: kv[0] in line_kwargs,
                {**_default["rect"], **style, **opt.get("style", {})}.items())
        }
        yName = opt["y"]

        if (("ylim" in opt) and (len(opt["ylim"]) > 1)):
            ylim = opt.get("ylim")

            ylim[0] = ylim[0] if ylim[0] != None else df[yName].min()
            ylim[1] = ylim[1] if ylim[1] != None else df[yName].max()
        else:
            ylim = [
                df[yName].min(),
                df[yName].max()
            ]

        def plot(ax):
            ax.fill(
                [xPos[0], xPos[0], xPos[1], xPos[1]],
                [ylim[0], ylim[1], ylim[1], ylim[0]],
                **st
            )
            return ax
        return plot
    return setData


def velocityPlot(style={}):
    def setData(df, opt):
        st = {**_default["arrow"], **style, **opt.get("style", {})}

        def plot(ax):
            # 時刻と位置0の組 を作る(d,0)
            x = df[opt["x"]] if "x" in opt else df.index
            y = [0. for i in x]

            ax.plot(x, y, color="gray")
            ax.quiver(x, y, df[opt["EW"]], df[opt["NS"]], scale=1, scale_units="y",
                      **st
                      )

            return ax
        return plot
    return setData


def velocityPlotRGB(style={}):
    def setData(df, opt):
        st = {**_default["arrow"], **style, **opt.get("style", {})}
        st.pop("color")

        def plot(ax):
            # 時刻と位置0の組 を作る(d,0)
            x = df[opt["x"]] if "x" in opt else df.index
            y = [0. for i in x]

            ax.plot(x, y, color="gray")
            ax.quiver(x, y, df[opt["EW"]], df[opt["NS"]], scale=1, scale_units="y",
                      color=df["rgb"],
                      **st
                      )

            return ax
        return plot
    return setData


def normalize(min, max):
    def f(x):
        if (x < min):
            return 0
        elif (max < x):
            return 1
        else:
            return (x-min)/(max-min)
    return f


def rgbScale(min, max):
    n = normalize(min, max)

    def f(x):
        scaled = n(x)
        if (scaled < 1/6):
            r = 1
            g = (6. * scaled)
            b = 0
        elif (scaled < 2/6):
            r = (-6 * scaled + 2)
            g = 1
            b = 0
        elif (scaled < 3/6):
            r = 0
            g = 1
            b = 6 * scaled - 2
        elif (scaled < 4/6):
            r = 0
            g = -6 * scaled + 4
            b = 1
        elif (scaled < 5/6):
            r = 6 * scaled - 4
            g = 0
            b = 1
        else:
            r = 1
            g = 0
            b = - 6 * scaled + 6

        return (r, g, b)
    return f
