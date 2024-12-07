# >= python 3.9
from time import sleep

from plan_client.server import Server
from plan_client.client import Client
from init_settings import (
    map4_set,
    map5_set,
    map6_set,
    map7_set,
)

from plan_client.planners.cvm_planner import CVMPlanner as MyPlanner

from threading import Thread

svr = Server("./plan_server/")


def auto_run(server, client, config, run=True):
    server.set_map(config["map"])
    if config["para"] is not None:
        server.set_pos(config["para"])

    server.restart()
    sleep(0.5)  # wait for server start

    server.init_menu()
    if config["para"] is not None:
        server.menu_action(["File", "ParaLoad"])

    if run:
        server.menu_action(["Run"])

    client.loop(server)


def batch_task(batch, ops, stop_at_first=False):
    for i in range(len(batch)):
        planner, config = batch[i]
        ops(planner, i)
        auto_run(svr, planner, config=config, run=False if stop_at_first and i == 0 else True)


def do_nothing(planner, i): ...


# 地图可视化
# from map_vis import MyWidget
# from PySide6 import QtCore, QtWidgets, QtGui
# from PySide6.QtGui import QColor


# app = QtWidgets.QApplication([])
# win = MyWidget()
# map = [[0 for i in range(1200)] for i in range(800)]


# def update_map(points, point_type, dpos):
#     global map
#     map = [[0 for i in range(1200)] for i in range(800)]
#     for idx, i in enumerate(points):
#         if i[1] + dpos[1] >= 800 or i[0] + dpos[0] >= 1200:
#             continue
#         map[i[1] + dpos[1]][i[0] + dpos[0]] = point_type[idx]
#     win.update(map)


batch = [
    *[
        (Client(MyPlanner(dict(robot=map["para"]["robot"])), 300), map)
        for map in [map4_set, map5_set, map6_set, map7_set]
    ]
]


if __name__ == "__main__":
    Thread(target=batch_task, args=(batch, do_nothing, True)).start()
    # win.show()
    # app.exec()
