# %%
import sys
from PySide6 import QtCore, QtWidgets, QtGui

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QImage, QPixmap, QColor

# QtCore
# QtWidgets
# QtGui


import colorsys
import random


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step

    return hls_colors


def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append([r, g, b])

    return rgb_colors


# %%
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.img = QtGui.QImage(1200, 800, QtGui.QImage.Format_RGB888)
        self.img.fill(QColor(0, 0, 0).rgb())

        self.lab = QtWidgets.QLabel("你好", self)
        self.lab.setPixmap(QPixmap.fromImage(self.img))
        self.resize(1200, 800)

        # self.colorMap = [QColor(0, 0, 0), QColor(0, 255, 255), QColor(0, 255, 0)]
        self.colorMap = [QColor(0, 0, 0)] + [QColor(*c) for c in ncolors (64)]
        # self.btn.

    def update(self, map):
        # print('here')
        for y in range(800):
            for x in range(1200):
                self.img.setPixelColor(x, y, self.colorMap[map[y][x]])
                # if map[y][x] == 1:

        self.lab.setPixmap(QPixmap.fromImage(self.img))


# %%
# x -> row
# y -> column
# arr[x][y]
# arr[y][x]

if __name__ == "__main__":
    app = QtWidgets.QApplication([])


# %%
if __name__ == "__main__":
    map = [[0 for i in range(1200)] for i in range(800)]

    for x in list(range(4)) + list(range(800 - 4, 800)):
        for y in range(1200):
            map[x][y] = 1

    w = MyWidget()
    # w.resize(800, 600)
    w.show()
    w.update(map)
    app.exec()

# %%

from math import acos, sqrt


def count_angle(v1, v2):
    inner = v1[0] * v2[0] + v1[1] * v2[1]
    cos_angle = inner / sqrt(v1[0] ** 2 + v1[1] ** 2) / sqrt(v2[0] ** 2 + v2[1] ** 2)
    angle = acos(cos_angle)
    return angle
