import math
import numpy as np


from ..c_structs import ServerInfo
from ..planner import Planner


r_robot = 20
max_distance = 300


def rng_at(l, r):
    if l > r:
        l, r = r, l
        return list(reversed(range(l, r + 1)))
    return list(range(l, r + 1))


def dist_collision(vel, **state):
    """
    max distance alone the curve (tra, rot) before collision
    args:
        vel: (2, n), search velocity, vel[0] is tra_vel, vel[1] is rot_vel
        **state: sensor data
            scans: (360)
            xy: (2, 360)
    """
    n_curve = vel.shape[1]
    ans = np.zeros(n_curve)

    idx = vel[0, :] > 0
    idx1 = idx & (vel[1, :] == 0)  # line
    idx2 = idx & (vel[1, :] > 0)  # curve left
    idx3 = idx & (vel[1, :] < 0)  # curve right

    n_left_curve = idx2.sum()
    n_right_curve = idx3.sum()

    if idx1.any():
        dist = state["scans"][0] - r_robot
        x, y = state["xy"][:, rng_at(-80, 80)]
        idx4 = abs(y) < r_robot
        xx, yy = x[idx4], y[idx4]
        dist = min(dist, np.min(xx - np.sqrt(r_robot**2 - yy**2)))
        ans[idx1] = dist

    if idx2.any():
        rot_centre_y = vel[0, idx2] / vel[1, idx2]
        radius = abs(rot_centre_y)
        x, y = state["xy"][:, rng_at(-30, 80)]

        dy = rot_centre_y[..., None] - y[None, ...].repeat(n_left_curve, 0)
        d = np.sqrt(dy**2 + x[None, ...] ** 2)

        idx5 = abs(d - radius[..., None]) < r_robot

        res1 = np.zeros(n_left_curve)
        for curve_idx, d in enumerate(d):
            # print(curve_idx, d[idx5[curve_idx]])
            if not idx5[curve_idx].any():
                res1[curve_idx] = math.pi * radius[curve_idx]
                continue
            dd = d[idx5[curve_idx]]
            xx = x[idx5[curve_idx]]
            ang0 = np.atan2(xx, dy[curve_idx][idx5[curve_idx]])
            ang1 = np.acos((radius[curve_idx] ** 2 + dd**2 - r_robot**2) / (2 * radius[curve_idx] * dd))
            ang = min(math.pi, np.min(ang0 - ang1))
            res1[curve_idx] = ang * radius[curve_idx]
        ans[idx2] = res1

    if idx3.any():
        rot_centre_y = vel[0, idx3] / vel[1, idx3]
        radius = abs(rot_centre_y)
        x, y = state["xy"][:, rng_at(-80, 30)]

        dy = rot_centre_y[..., None] - y[None, ...].repeat(n_right_curve, 0)
        d = np.sqrt(dy**2 + x[None, ...] ** 2)

        idx6 = abs(d - radius[..., None]) < r_robot
        res2 = np.zeros(n_right_curve)
        for curve_idx, d in enumerate(d):
            if not idx6[curve_idx].any():
                res2[curve_idx] = math.pi * radius[curve_idx]
                continue
            dd = d[idx6[curve_idx]]
            xx = x[idx6[curve_idx]]
            ang0 = np.atan2(xx, -dy[curve_idx][idx6[curve_idx]])
            ang1 = np.acos((radius[curve_idx] ** 2 + dd**2 - r_robot**2) / (2 * radius[curve_idx] * dd))
            ang = min(math.pi, np.min(ang0 - ang1))
            res2[curve_idx] = ang * radius[curve_idx]
        ans[idx3] = res2

    # * cases that need turn around
    if (ans < 30).sum() > len(ans) * 0.7:
        print("here")
        idx0 = vel[0, :] == 0
        ans[idx0] = abs(vel[1][idx0]) * max_distance * 2

    # np.set_printoptions(suppress=True)
    # f = np.concatenate([vel, ans[None, ...]], 0).transpose()
    # print(f)

    if (ans < -1e-6).any():
        # np.save("err_vel.npy", vel)
        np.save("err_dist.npy", np.concatenate([vel, ans[None, ...]], 0))
        raise ArithmeticError(
            "distance should not be negative, this error may caused by some *computation dead area*, check the data saved in `err_vel.npy` and `err_dist.npy`"
        )
    return ans / max_distance


def velocity(vel, **state):
    return vel[0] / 55


def head(vel, **state):
    return 1 - np.abs(state["target_angle"] - vel[1] * 0.2) / np.pi
    ...


class CVM:
    """
    search_space: (2, n), search_space[0] is tra_vel, search_space[1] is rot_vel
    """

    def __init__(self, acc_tra, acc_rot, *, rot_vel_bound=(-1, 1), tra_vel_bound=(0, 50)):
        self.tra_vel_bound = tra_vel_bound
        self.rot_vel_bound = rot_vel_bound

        self.acc_tra = np.array(acc_tra)
        self.acc_rot = np.array(acc_rot)
        t = [self.acc_tra[None, ...].repeat(len(self.acc_rot), 0).reshape(-1), self.acc_rot.repeat(len(self.acc_tra))]
        self.search_space = np.stack(t)

        self.target_funcs = []

        # print(self.search_space)

    def add_target_func(self, func, w=1):
        self.target_funcs.append((func, w))

    def next(self, vel, **state):
        # print("shape",self.search_space.shape)
        vel = self.search_space + np.array(vel)[..., None]
        vel = np.stack([np.clip(vel[0], *self.tra_vel_bound), np.clip(vel[1], *self.rot_vel_bound)])
        vel = np.unique(vel.transpose(), axis=0).transpose()

        # ? real velocity
        vel[0][vel[0] > 0] += 5

        values = np.zeros(vel.shape[1])
        for func, w in self.target_funcs:
            values += w * func(vel, **state)

        tar_vel = vel[:, values.argmax()]

        if tar_vel[0] > 0:
            tar_vel[0] -= 5

        return tar_vel


class CVMPlanner(Planner):
    def __init__(self, para=None):
        super().__init__(para)
        self.acc_tra = np.concatenate([np.linspace(-20, 20, 13), np.linspace(-50, -20, 13)])
        self.acc_rot = np.linspace(-1, 1, 17)

        self.cvm = CVM(self.acc_tra, self.acc_rot)
        self.cvm.add_target_func(dist_collision)
        self.cvm.add_target_func(velocity)
        self.cvm.add_target_func(head, 1)

    def plan(self, ser_info: ServerInfo):
        scans = np.array(ser_info.obstacle)
        deg = np.array(list(range(360)))
        xy = scans[None, ...] * np.stack([np.cos(deg / 180 * np.pi), np.sin(deg / 180 * np.pi)])

        try:
            vel = self.cvm.next(
                (self.tra_vel, self.rot_vel),
                scans=scans,
                xy=xy,
                target_angle=ser_info.target_angle,
            )
        except ArithmeticError as r:
            np.save("err_scans.npy", scans)
            np.save("err_vel.npy", np.array([self.tra_vel, self.rot_vel]))
            raise r

        self.tra_vel, self.rot_vel = vel
        print(self.tra_vel, self.rot_vel)

        # if self.tra_vel > 0:
        #     self.tra_vel -= 5

        # if ser_info.timestamp > 78:
        #     np.save("scans.npy", scans)
        #     np.save("vel.npy",np.array([self.tra_vel, self.rot_vel]))
        #     self.need_break = True

        if ser_info.detect_object:
            ...
