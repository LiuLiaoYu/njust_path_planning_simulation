import math
from .c_structs import Point, Pose, ServerInfo, ClientInfo, reset


class Planner:
    x: float  # 位姿 x
    y: float  # 位姿 y
    ori: float  # 位姿 theta 转角
    rot_vel: float  # 角速度
    tra_vel: float  # 线速度
    need_break: bool  # 置真会中止当前规划
    plan_traj: list[Point]  # 规划轨迹

    def __init__(self, para=None):
        self.FRAME_DUR = 0.2  # 每帧间隔
        self.tra_vel = 0
        self.rot_vel = 0
        self.need_break = False
        self.para_setting = para
        self.plan_traj = None

    def run(self, ser_info: ServerInfo, cli_info: ClientInfo):
        cli_info.timestamp = ser_info.timestamp
        cli_info.run_status = ser_info.run_status

        # 定位
        self.locate(ser_info)
        cli_info.pred_pose = Pose(int(self.x), int(self.y), self.ori)

        # 规划
        if ser_info.timestamp > 0:
            self.plan(ser_info)
        cli_info.tra_vel = self.tra_vel
        cli_info.rot_vel = self.rot_vel

        # 可视化规划路径
        if self.plan_traj is not None:
            reset(cli_info.pred_traj)
            for i in range(min(len(self.plan_traj), 100)):
                cli_info.pred_traj[i] = Point(*self.plan_traj[i])

        return self.need_break

    def locate(self, ser_info: ServerInfo):
        # * motion location
        if ser_info.timestamp == 0:
            if self.para_setting is not None:
                # server 返回的 initial_pose 可能是不准的，可以通过 para 传进来
                init_pose = self.para_setting["robot"]
            else:
                init_pose = ser_info.initial_pose
            self.x = init_pose.x
            self.y = init_pose.y
            self.ori = init_pose.ori
        else:
            angle = self.rot_vel * self.FRAME_DUR
            distance = 0 if self.tra_vel == 0 else (self.tra_vel + 5) * self.FRAME_DUR
            # if ser_info.timestamp > 1:
            self.ori += angle
            self.x += distance * math.cos(self.ori)
            self.y += distance * math.sin(self.ori)

    def plan(self, ser_info: ServerInfo):
        self.tra_vel = 10
        self.rot_vel = 0.1
        if ser_info.detect_object:
            self.tra_vel = 20
            self.rot_vel = ser_info.target_angle
