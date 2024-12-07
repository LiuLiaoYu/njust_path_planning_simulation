import json
from pathlib import Path

from psutil import Process
from shutil import copyfile
from subprocess import Popen

from socket import socket, AF_INET, SOCK_STREAM

from win32con import WM_COMMAND
from win32gui_struct import EmptyMENUITEMINFO, UnpackMENUITEMINFO
from win32gui import GetMenuItemInfo, GetMenuItemCount, GetMenu, FindWindow, PostMessage


def get_win_menu_item_info(hmenu, i):
    mii, extra = EmptyMENUITEMINFO()
    GetMenuItemInfo(hmenu, i, True, mii)
    info = UnpackMENUITEMINFO(mii)
    return info


def get_win_menu(hmenu):
    menu = {}
    menu_item_num = GetMenuItemCount(hmenu)

    for i in range(menu_item_num):
        info = get_win_menu_item_info(hmenu, i)
        if info.hSubMenu == 0:
            menu[info.text] = info.wID
        else:
            menu[info.text] = get_win_menu(info.hSubMenu)

    return menu


class Server:
    def __init__(self, server_dir):
        self.server_dir = Path(server_dir)
        self.default_map = self.server_dir / "bitmap1.jpg"
        self.cache_file = self.server_dir / "cache.json"
        self.socket = ("127.0.0.1", 8888)
        if self.cache_file.exists():
            self.load_cache()
        else:
            self.cache_data = {"map_path": "", "server_pid": None}

    def load_cache(self):
        with open(self.cache_file, "r", encoding="utf8") as f:
            self.cache_data = json.load(f)

    def dump_cache(self):
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(self.cache_data, f)

    def set_map(self, jpg_path):
        # * map size: 1200 * 800, initially load `bitmap1.jpg`
        jpg_path = Path(jpg_path)
        if not jpg_path.is_file():
            print(f"use cached map: {self.cache_data['map_path']}")
        elif jpg_path != Path(self.cache_data["map_path"]):
            copyfile(jpg_path, self.default_map)
            self.cache_data["map_path"] = str(jpg_path)
            print(f"set map: {self.cache_data['map_path']}")
        else:
            print(f"use map: {self.cache_data['map_path']}")

    def set_pos(self, para):
        with open(self.server_dir / "para.txt", "w", encoding="utf-8") as f:
            f.write(f"{para['robot'].x} {para['robot'].y} {para['robot'].ori}\n")
            f.write(f"{para['target'].x} {para['target'].y}\n")
            if para.get("obstacles", None) is not None:
                f.write(f"{len(para['obstacles'])}\n")
                for i in range(len(para["obstacles"])):
                    f.write(f"{para['obstacles'][i].x} {para['obstacles'][i].y} {para['obstacles'][i].ori}\n")

    def kill(self):
        # use last pid cache
        if self.cache_data["server_pid"] is not None:  # use last pid cache
            pid = self.cache_data["server_pid"]
            try:
                proc = Process(pid)  # may not valid
                if proc.name().endswith("Plan_Server.exe"):
                    print(f"kill server(pid:{pid}, cached) for restart")
                    proc.kill()
                    return
            except:
                ...

        # traverse processes to kill
        # for proc in psutil.process_iter():
        #     if proc.name().endswith("Plan_Server.exe"):
        #         pid = proc.pid
        #         print(f"kill server(pid:{pid}) for restart")
        #         proc.kill()
        #         break

    def start(self):
        try:
            proc = Popen(self.server_dir / "Plan_Server.exe")
            self.cache_data["server_pid"] = proc.pid
            print("start server")
            self.dump_cache()
        except:
            print("falied to start server")
            exit(-1)

    def restart(self):
        self.kill()
        self.start()

    def connect(self):
        try:
            s = socket(family=AF_INET, type=SOCK_STREAM)
            s.connect(self.socket)
        except:
            print("connect failed! check if the server has started.")
            exit(-1)
        return s

    def init_menu(self):
        hwnd = FindWindow(None, "Motion_Server")
        hmenu = GetMenu(hwnd)
        self.menu = get_win_menu(hmenu)
        self.hwnd = hwnd

    def menu_action(self, actions):
        cmd_id = self.menu
        for i in actions:
            cmd_id = cmd_id[i]

        PostMessage(self.hwnd, WM_COMMAND, cmd_id, 0)
