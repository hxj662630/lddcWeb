# SPDX-FileCopyrightText: Copyright (c) 2024 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: GPL-3.0-only
import json
import os
import re
import shlex
import subprocess
import sys
import time
from abc import abstractmethod
from collections import deque
from copy import deepcopy
from random import SystemRandom
from typing import Literal

import psutil
# from PySide6.QtCore import (
#     QCoreApplication,
#     QEventLoop,
#     QMutex,
#     QObject,
#     QRunnable,
#     QSharedMemory,
#     Qt,
#     QTimer,
#     Signal,
# )
# from PySide6.QtNetwork import (
#     QHostAddress,
#     QLocalServer,
#     QLocalSocket,
#     QTcpServer,
#     QTcpSocket,
# )

from backend.calculate import find_closest_match
from backend.fetcher import get_lyrics
from backend.lyrics import Lyrics
from utils.args import args
from utils.enum import LyricsFormat, LyricsType, Source
from utils.logger import DEBUG, logger
from utils.paths import auto_save_dir, command_line
from utils.utils import escape_filename, get_artist_str, has_content
# from view.desktop_lyrics import DesktopLyrics, DesktopLyricsWidget

random = SystemRandom()
api_version = 1


class ServiceInstanceSignal(QObject):
    handle_task = Signal(dict)
    stop = Signal()


class ServiceInstanceBase(QRunnable):

    def __init__(self, service: "LDDCService", instance_id: int, client_id: int, pid: int | None = None) -> None:
        super().__init__()
        self.service = service
        self.instance_id = instance_id
        self.pid = pid
        self.client_id = client_id

        self.signals = ServiceInstanceSignal()
        self.signals.stop.connect(self.stop)

    @abstractmethod
    def handle_task(self, task: dict) -> None:
        ...

    @abstractmethod
    def init(self) -> None:
        ...

    def stop(self) -> None:
        self.loop.quit()
        logger.info("Service instance %s stopped", self.instance_id)
        instance_dict_mutex.lock()
        del instance_dict[self.instance_id]
        instance_dict_mutex.unlock()

    def run(self) -> None:
        logger.info("Service instance %s started", self.instance_id)
        self.signals.handle_task.connect(self.handle_task)
        self.loop = QEventLoop()
        self.init()
        self.loop.exec()


instance_dict: dict[int, ServiceInstanceBase] = {}
instance_dict_mutex = QMutex()


def clean_dead_instance() -> bool:
    to_stop = []
    instance_dict_mutex.lock()
    for instance_id, instance in instance_dict.items():
        if instance.pid is not None and not psutil.pid_exists(instance.pid):
            to_stop.append(instance_id)
    instance_dict_mutex.unlock()

    for instance_id in to_stop:
        instance_dict[instance_id].signals.stop.emit()
    return bool(to_stop)


def check_any_instance_alive() -> bool:
    clean_dead_instance()
    return bool(instance_dict)


class Client:
    def __init__(self, socket: QTcpSocket | QLocalSocket) -> None:
        self.socket = socket
        self.buffer = bytearray()


# class LDDCService(QObject):
#     handle_task = Signal(int, dict)
#     instance_del = Signal()
#     send_msg = Signal(int, str)

#     def __init__(self) -> None:
#         super().__init__()
#         self.q_server = QLocalServer(self)
#         self.q_server_name = "LDDCService"
#         self.socketserver = None
#         self.shared_memory = QSharedMemory(self)
#         self.shared_memory.setKey("LDDCLOCK")

#         self.clients: dict[int, Client] = {}
#         self.start_service()

#         from utils.exit_manager import exit_manager
#         exit_manager.close_signal.connect(self.stop_service, Qt.ConnectionType.BlockingQueuedConnection)

#     def start_service(self) -> None:

#         if args.get_service_port and not self.shared_memory.attach():
#             cmd = shlex.split(command_line, posix=False)
#             arguments = [re.sub(r'"([^"]+)"', r'\1', arg) for arg in [cmd[0]] + ([*cmd[1:], "--not-show"] if len(cmd) > 1 else ["--not-show"])]

#             # 注意在调试模式下无法新建一个独立进程
#             logger.info("在独立进程中启动LDDC服务,  命令行参数：%s", arguments)
#             subprocess.Popen(arguments,  # noqa: S603
#                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                              close_fds=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)

#             wait_time = 0
#             while not self.shared_memory.attach():
#                 time.sleep(0.05)
#                 wait_time += 0.05
#                 if wait_time > 5:
#                     logger.error("LDDC服务启动失败")
#                     sys.exit(1)
#             logger.info("LDDC服务启动成功")

#         if self.shared_memory.attach() or not self.shared_memory.create(1):
#             # 说明已经有其他LDDC服务启动
#             logger.info("LDDC服务已经启动")
#             q_client = QLocalSocket()
#             q_client.connectToServer(self.q_server_name)
#             if not q_client.waitForConnected(1000):
#                 logger.error("LDDC服务连接失败")
#                 sys.exit(1)
#             if args.get_service_port:
#                 message = "get_service_port"
#             elif args.show is False:
#                 sys.exit(0)
#             else:
#                 message = "show"
#             q_client.write(message.encode())
#             q_client.flush()
#             logger.info("发送消息：%s", message)
#             if q_client.waitForReadyRead(1000):
#                 response_data = q_client.readAll().data()
#                 if isinstance(response_data, memoryview):
#                     response_data = response_data.tobytes()
#                 response = response_data.decode()
#                 logger.info("收到服务端消息：%s", response)
#                 if args.get_service_port:
#                     print(response)  # 输出服务端监听的端口  # noqa: T201
#                     sys.exit(0)
#                 else:
#                     self.q_server.close()
#                     sys.exit(0)
#             else:
#                 logger.error("LDDC服务连接失败")
#                 sys.exit(1)
#         else:
#             self.q_server.listen(self.q_server_name)
#             # 找到一个可用的端口
#             self.socketserver = QTcpServer(self)
#             while True:
#                 port = random.randint(10000, 65535)  # 随机生成一个端口
#                 if self.socketserver.listen(QHostAddress("127.0.0.1"), port):
#                     self.socket_port = port
#                     break
#                 logger.error("端口%s被占用", port)

#             logger.info("LDDC服务启动成功, 端口: %s", self.socket_port)
#             self.q_server.newConnection.connect(self.on_q_server_new_connection)
#             self.socketserver.newConnection.connect(self.socket_on_new_connection)

#             self.check_any_instance_alive_timer = QTimer(self)
#             self.check_any_instance_alive_timer.timeout.connect(self._clean_dead_instance)
#             self.check_any_instance_alive_timer.start(1000)

#             self.send_msg.connect(self.socket_send_message)

#     def stop_service(self) -> None:
#         self.q_server.close()
#         if self.socketserver:
#             self.socketserver.close()
#         self.shared_memory.detach()
#         self.check_any_instance_alive_timer.stop()

#     def on_q_server_new_connection(self) -> None:
#         logger.info("q_server_new_connection")
#         client_connection = self.q_server.nextPendingConnection()
#         if client_connection:
#             client_connection.readyRead.connect(self.q_server_read_client)

#     def q_server_read_client(self) -> None:
#         client_connection = self.sender()
#         if not isinstance(client_connection, QLocalSocket):
#             return
#         response_data = client_connection.readAll().data()
#         if isinstance(response_data, memoryview):
#             response_data = response_data.tobytes()
#         response = response_data.decode()
#         logger.info("收到客户端消息:%s", response)
#         match response:
#             case "get_service_port":
#                 client_connection.write(str(self.socket_port).encode())
#                 client_connection.flush()
#                 client_connection.disconnectFromServer()
#             case "show":
#                 def show_main_window() -> None:
#                     from view.main_window import main_window
#                     main_window.show_window()
#                 in_main_thread(show_main_window)
#                 client_connection.write(b"message_received")
#                 client_connection.flush()
#                 client_connection.disconnectFromServer()
#             case _:
#                 logger.error("未知消息：%s", response)

#     def socket_on_new_connection(self) -> None:
#         if not self.socketserver:
#             return
#         client_socket = self.socketserver.nextPendingConnection()
#         client_id = int(f"{id(client_socket) % (10 ** 5)}{(int(time.time() * 1000) % (10 ** 4))}")
#         logger.info("客户端连接，客户端id：%s", client_id)
#         self.clients[client_id] = Client(client_socket)
#         client_socket.readyRead.connect(lambda: self.socket_read_data(client_id))
#         client_socket.disconnected.connect(lambda: self.handle_disconnection(client_id))

#     def handle_disconnection(self, client_id: int) -> None:
#         client_socket = self.clients[client_id].socket
#         if isinstance(client_socket, QTcpSocket):
#             client_socket.deleteLater()
#         del self.clients[client_id]

#     def socket_read_data(self, client_id: int) -> None:
#         """处理客户端发送的数据(前4字节应为消息长度)"""
#         if self.clients[client_id].socket.bytesAvailable() > 0:
#             self.clients[client_id].buffer.extend(self.clients[client_id].socket.readAll().data())

#             while not len(self.clients[client_id].buffer) < 4:

#                 message_length = int.from_bytes(self.clients[client_id].buffer[:4], byteorder='big')  # 获取消息长度(前四字节)

#                 if len(self.clients[client_id].buffer) < 4 + message_length:
#                     break

#                 message_data = self.clients[client_id].buffer[4:4 + message_length]
#                 self.clients[client_id].buffer = self.clients[client_id].buffer[4 + message_length:]

#                 self.handle_socket_message(message_data, client_id)

#     def handle_socket_message(self, message_data: bytes, client_id: int) -> None:
#         data = message_data.decode()
#         try:
#             json_data = json.loads(data)
#             if not isinstance(json_data, dict) or "task" not in json_data:
#                 logger.error("数据格式错误: %s", data)
#                 return
#         except json.JSONDecodeError:
#             logger.exception("JSON解码错误: %s", data)
#             return
#         if logger.level <= DEBUG:
#             logger.debug("收到客户端消息：%s", json.dumps(json_data, ensure_ascii=False, indent=4))
#         if "id" not in json_data:
#             match json_data["task"]:
#                 case "new_desktop_lyrics_instance":
#                     instance_id = random.choice(list(set(range(1024 + len(instance_dict))) - set(instance_dict.keys())))
#                     instance_dict_mutex.lock()
#                     instance_dict[instance_id] = DesktopLyricsInstance(self, instance_id, json_data, client_id)
#                     instance_dict_mutex.unlock()
#                     threadpool.startOnReservedThread(instance_dict[instance_id])
#                     logger.info("创建新实例：%s", instance_id)
#                     response = {"v": api_version, "id": instance_id}
#                     self.socket_send_message(client_id, json.dumps(response))
#         elif json_data["id"] in instance_dict:
#             if json_data["task"] == "del_instance":
#                 instance_dict[json_data["id"]].signals.stop.emit()
#                 self.instance_del.emit()
#             else:
#                 instance_dict[json_data["id"]].signals.handle_task.emit(json_data)

#     def socket_send_message(self, client_id: int, response: str) -> None:
#         """向客户端发送消息(前4字节应为消息长度)"""
#         logger.debug("%s 发送响应：%s", client_id, response)
#         if client_id not in self.clients:
#             logger.error("客户端ID不存在：%s, self.clients: %s", client_id, self.clients)
#         client_socket = self.clients[client_id].socket
#         response_bytes = response.encode('utf-8')
#         response_length = len(response_bytes)
#         length_bytes = response_length.to_bytes(4, byteorder='big')

#         client_socket.write(length_bytes + response_bytes)
#         client_socket.flush()

#     def _clean_dead_instance(self) -> None:
#         if clean_dead_instance():
#             self.instance_del.emit()
