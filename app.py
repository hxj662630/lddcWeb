# SPDX-FileCopyrightText: Copyright (c) 2024 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: GPL-3.0-only
# from PySide6.QtCore import QThread
# from PySide6.QtWidgets import QApplication
# from backend.service import LDDCService
# from utils.exit_manager import exit_manager
from utils.enum import SearchType
from flask import Flask, jsonify, request
from backend.api import qm_search
from backend.lyrics import Lyrics, LyricsData
from backend.fetcher.qm import get_lyrics
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/api/greet', methods=['GET'])
def greet():
    title = request.args.get('title', 'World')
    return jsonify({'message': f'Hello, {title}!'})

@app.route('/api/search', methods=['GET'])
def qrcsearch():
    keyword = request.args.get('keyword', 'World')
    searchRes = qm_search(keyword, SearchType.SONG, 1)
    if searchRes:
        lyrics = Lyrics(searchRes[0])
        get_lyrics(lyrics)
        # lyricRes = qm_get_lyrics(searchRes[0].get('title'), searchRes[0].get('artist'), searchRes[0].get('album'), searchRes[0].get('id'), searchRes[0].get('duration'))
        # serializable_list = [str(item) for item in lyrics]  # 将所有项转换为字符串
        serializable_list = json.dumps(lyrics,ensure_ascii=False)
        return serializable_list
        # return json.dumps(lyrics)
    else:
        jsonify({'message': 'no result'})

app.run(host = '0.0.0.0', port = 9000)
