# SPDX-FileCopyrightText: Copyright (c) 2024 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: GPL-3.0-only
# from PySide6.QtCore import QThread
# from PySide6.QtWidgets import QApplication
# from backend.service import LDDCService
from res import resource_rc
# from utils.exit_manager import exit_manager
from utils.enum import SearchType
from flask import Flask, jsonify, request
from backend.api import qm_search
from backend.lyrics import Lyrics, LyricsData
from backend.fetcher.qm import get_lyrics
import json


resource_rc.qInitResources()


if __name__ == "__main__":

    # app = QApplication(sys.argv)

    appW = Flask(__name__)

    @appW.route('/api/greet', methods=['GET'])
    def greet():
        title = request.args.get('title', 'World')
        return jsonify({'message': f'Hello, {title}!'})
    
    @appW.route('/api/search', methods=['GET'])
    def qrcsearch():
        keyword = request.args.get('keyword', 'World')
        searchRes = qm_search(keyword, SearchType.SONG, 1)
        if searchRes:
            lyrics = Lyrics(searchRes[0])
            get_lyrics(lyrics)
            # lyricRes = qm_get_lyrics(searchRes[0].get('title'), searchRes[0].get('artist'), searchRes[0].get('album'), searchRes[0].get('id'), searchRes[0].get('duration'))
            serializable_list = [str(item) for item in lyrics]  # 将所有项转换为字符串
            return jsonify(lyrics)
            # return json.dumps(lyrics)
        else:
            jsonify({'message': 'no result'})
        


    appW.run(debug=True)
    # if args.get_service_port:
        # 如果是获取服务端口,则只需实例化LDDCService(会获取并打印另一个LDDC进程服务端口),然后退出
        # LDDCService()
        # sys.exit()

    # show = args.show

    # 启动服务线程
    # service = LDDCService()
    # service_thread = QThread(app)
    # exit_manager.threads.append(service_thread)
    # service.moveToThread(service_thread)
    # service_thread.start()
    # service.instance_del.connect(exit_manager.close_event)

    # 加载翻译
    # load_translation(False)
    # 显示主窗口(如果需要)
    # if show:
    #     from view.main_window import main_window
    #     main_window.show()

    # 检查更新
    # from utils.data import cfg
    # if cfg["auto_check_update"]:
    #     from view.update import check_update
    #     check_update(True, QApplication.translate("CheckUpdate", "LDDC主程序"), "chenmozhijin/LDDC", __version__)

    # 进入事件循环
    # sys.exit(app.exec())
