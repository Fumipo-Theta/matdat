import os
import matplotlib.pyplot as plt


def __safe_filename(filename: str) -> str:
    return filename.replace("/", "").replace("\\", "")


def actionSavePNG(directory, filename):
    # パスが有効かどうかを検証し, ディレクトリがなければ作成する
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return lambda postfix="": plt.savefig(directory+__safe_filename(filename+postfix+'.png'))
