import os
import glob
import re
from .util import pip, tee, mapping, filtering, reducing
from IPython.display import display

"""
与えられた正規表現パターン `patterns` に対し,
パターンにマッチするパスのみを返す.
デフォルトではあらゆるパスにマッチする.

指定したディレクトリ `dirPath` 以下を再帰的に探索し,
ディレクトリとファイルパスの一覧を取得する.
"""


def getAllSubPath(_directory):
    directory = _directory if re.search(
        "/$", _directory) != None else _directory + "/"
    return glob.glob(directory+"**", recursive=True)


def isMatchAll(patterns):
    return lambda s: reducing(lambda a, b: a and b)(
        mapping(lambda pattern: re.search(pattern, s) != None)(patterns)
    )(True)


class PathList:
    def __init__(self, pathList):
        self.paths = pathList

    def directories(self):
        return pip(
            filtering(os.path.isdir),
            list,
            tee(
                pip(
                    enumerate,
                    list,
                    display
                )
            )
        )(self.paths)

    def files(self):
        return pip(
            filtering(os.path.isfile),
            list,
            tee(
                pip(
                    enumerate,
                    list,
                    display
                )
            )
        )(self.paths)


def getFileList(*patterns):
    return lambda dirPath: pip(
        getAllSubPath,
        filtering(isMatchAll(patterns)),
        list,
        PathList
    )(dirPath)
