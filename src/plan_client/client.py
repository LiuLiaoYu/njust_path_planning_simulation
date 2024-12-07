from .c_structs import ServerInfo, ClientInfo
from time import sleep


class Client:
    def __init__(self, planner, frame_limit=-1, **args):
        self.planner = planner
        self.ser_info = ServerInfo()
        self.cli_info = ClientInfo()
        self.frame_limit = frame_limit
        self.run_status = 1

        self.args = args

    def loop(self, server):
        s = server.connect()  # socket connect
        s.settimeout(0.2)

        print("server connected")
        frame = 0

        while True:
            if self.frame_limit > 0 and frame >= self.frame_limit:
                print("**frame limit**")
                break
            # non-block recv
            try:
                recv_data = s.recv(1024)
            except:
                if self.run_status == 2:
                    print("paused")
                    self.run_status = 3
                sleep(0.03)
                continue

            self.ser_info.load(recv_data)

            if self.ser_info.run_status == 0:
                print("**server shutdown**")
                break
            if self.ser_info.collision:
                print("**collision happened**")
                break
            if self.ser_info.task_finish:
                print(f"**find object, total frames: {self.ser_info.timestamp}**")
                break

            if self.ser_info.timestamp == 0:
                self.run_status = 2
                print("start running")

            if self.run_status == 3:  # restore from pause
                self.run_status = 2

            need_break = self.planner.run(self.ser_info, self.cli_info)

            if self.args.get("update_map", None) is not None:
                self.args["update_map"](self.planner.points, self.planner.point_type, self.planner.dpos)

            if need_break:
                break

            s.send(self.cli_info.dump())
            frame += 1
        s.close()
