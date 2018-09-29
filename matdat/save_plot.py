import os
import matplotlib.pyplot as plt


def actionSavePNG(directory, filename):
    # パスが有効かどうかを検証し, ディレクトリがなければ作成する
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return lambda str="": plt.savefig(directory+filename+str+'.png')
