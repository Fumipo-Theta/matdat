from abc import ABC, abstractmethod


class ILazyReader(ABC):
    def __ini__(self):
        pass

    @abstractmethod
    def setPath(self, path):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def assemble(self):
        pass

    @abstractmethod
    def getDataFrame(self):
        pass
