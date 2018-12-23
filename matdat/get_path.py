import os
import glob
import re
from func_helper import pip, tee, identity
import func_helper.func_helper.iterator as it

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
    return lambda s: it.reducing(lambda a, b: a and b)(True)(
        it.mapping(lambda pattern: re.search(pattern, s) != None)(patterns)
    )


class PathList:
    def __init__(self, pathList):
        self.paths = pathList

    def directories(self, verbose=False):
        return pip(
            it.filtering(os.path.isdir),
            list,
            tee(
                pip(
                    enumerate,
                    list,
                    print if verbose else identity
                )
            )
        )(self.paths)

    def files(self, verbose=False):
        return pip(
            it.filtering(os.path.isfile),
            list,
            tee(
                pip(
                    enumerate,
                    list,
                    print if verbose else identity
                )
            )
        )(self.paths)


def getFileList(*patterns):
    return lambda dirPath: pip(
        getAllSubPath,
        it.filtering(isMatchAll(patterns)),
        list,
        PathList
    )(dirPath)
