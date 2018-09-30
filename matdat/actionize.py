def actionize(function_for_plot):
    return lambda arg: lambda df, opt: lambda ax: fnction_for_plot(ax, df, opt, arg)
