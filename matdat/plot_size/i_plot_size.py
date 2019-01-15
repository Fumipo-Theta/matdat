import abc


class IPlotSize(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def use(self)->dict:
        pass
