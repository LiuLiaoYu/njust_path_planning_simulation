from plan_client.c_structs import Point, Pose
from copy import deepcopy


default_set = {
    "map": "./plan_server/map0.jpg",  # 地图 jpg 文件
    "para": {
        "robot": Pose(30, 200, 0),  # 机器人初始位姿
        "target": Point(140, 690),  # 目标位置
        "obstacles": [  # 动态障碍物
            Pose(1060, 704, -0.6202),
            Pose(1057, 107, -2.8555),
            Pose(538, 645, -0.5831),
            Pose(190, 709, -2.7150),
            Pose(378, 83, 3.1416),
        ],
    },
}


map4_set = {
    "map": "./plan_server/map4.jpg",
    "para": {
        "robot": Pose(266, 182, 0),
        "target": Point(928, 604),
    },
}


map5_set = {
    "map": "./plan_server/map5.jpg",
    "para": {
        "robot": Pose(261, 626, 0),
        "target": Point(810, 229),
    },
}

map6_set = {
    "map": "./plan_server/map6.jpg",
    "para": {
        "robot": Pose(310, 116, 0.774791),
        "target": Point(878, 695),
    },
}


map7_set = {
    "map": "./plan_server/map7.jpg",
    "para": {
        "robot": Pose(310, 116, 0.774791),
        "target": Point(878, 695),
    },
}
