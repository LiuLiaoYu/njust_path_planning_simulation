from ctypes import Structure, memmove, memset, string_at, addressof, c_double, c_uint8, Array, c_int16, sizeof


def load(tar, bytes):
    memmove(addressof(tar), bytes, sizeof(tar.__class__))


def dump(tar):
    return string_at(addressof(tar), sizeof(tar.__class__))


def reset(tar):
    memset(addressof(tar), 0, sizeof(tar.__class__))


class ExtStruct(Structure):

    def load(self, bytes):
        load(self, bytes)

    def dump(self):
        return dump(self)

    def reset(self):
        reset(self)

    def __repr__(self):
        fields = {f[0]: x if not isinstance((x := getattr(self, f[0])), Array) else list(x) for f in self._fields_}
        return str(fields)


class Pose(ExtStruct):
    x: c_int16
    y: c_int16
    ori: c_double
    _fields_ = [
        ("x", c_int16),
        ("y", c_int16),
        ("ori", c_double),
    ]


class Point(ExtStruct):
    x: c_int16
    y: c_int16
    _fields_ = [
        ("x", c_int16),
        ("y", c_int16),
    ]


class ServerInfo(ExtStruct):
    timestamp: c_int16
    run_status: c_int16
    task_finish: c_uint8
    detect_object: c_uint8
    collision: c_uint8
    obstacle: Array[c_int16]
    initial_pose: Pose
    initial_dest: Point
    target_angle: c_double
    _fields_ = [
        ("timestamp", c_int16),  # 时间戳，从0开始
        ("run_status", c_int16),  # 运行状态
        ("task_finish", c_uint8),  # 任务完成标志
        ("detect_object", c_uint8),  # 检测目标标志，目标和机器人间连线无障碍物
        # 注意 1.如果没有移动则始终为 0; 2.如果距离太大也为 0
        ("collision", c_uint8),  # 碰撞标志
        ("obstacle", c_int16 * 360),  # 360度测距线，0为前进方向，顺时针，最大半径为 500
        ("initial_pose", Pose),  # 起始位姿，?可能会失效?
        ("initial_dest", Point),  # 终止位置
        ("target_angle", c_double),  # 目标与前进方向的夹角
    ]


class ClientInfo(ExtStruct):
    timestamp: c_int16
    run_status: c_int16
    tra_vel: c_double
    rot_vel: c_double
    pred_pose: Pose
    pred_traj: Array[Point]
    _fields_ = [
        ("timestamp", c_int16),  # 时间戳
        ("run_status", c_int16),  # 运行状态
        ("tra_vel", c_double),  # 速度，cm/s，[0,50]
        ("rot_vel", c_double),  # 角速度，rad/s，[-1, 1]
        ("pred_pose", Pose),  # 估计位姿(可视化)
        ("pred_traj", Point * 100),  # 规划路径(可视化，最多100个节点)
    ]


def debug(c_structure):
    if isinstance(c_structure, Structure):
        print(c_structure)
    elif isinstance(c_structure, Array):
        print(list(c_structure))
    else:
        print(c_structure)
