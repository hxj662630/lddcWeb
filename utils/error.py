# SPDX-FileCopyrightText: Copyright (c) 2024 沉默の金 <cmzj@cmzj.org>
# SPDX-License-Identifier: GPL-3.0-only


class ErrorMsgTranslator():
    """错误信息翻译器"""

    def translate(self, msg: str) -> str:
        """翻译错误信息

        :param msg: 错误信息
        :return: 错误信息
        """
        match msg:
            case "没有可解密的数据":
                return self.tr("没有可解密的数据")
            case "无效的加密数据类型":
                return self.tr("无效的加密数据类型")
            case "解密失败":
                return self.tr("解密失败")
            case "没有获取到可用的歌词":
                return self.tr("没有获取到可用的歌词")
            case _:
                if "请求歌词失败" in msg:
                    msg = msg.replace("请求歌词失败", self.tr("请求歌词失败"))

                if "没有找到歌词" in msg:
                    msg = msg.replace("没有找到歌词", self.tr("没有找到歌词"))

                if "JSON歌词数据缺少必要的键" in msg:
                    msg = msg.replace("JSON歌词数据缺少必要的键", self.tr("JSON歌词数据缺少必要的键"))

                if "JSON歌词数据中包含值类型不正确的键" in msg:
                    msg = msg.replace("JSON歌词数据中包含值类型不正确的键", self.tr("JSON歌词数据中包含值类型不正确的键"))

                if "JSON歌词数据中包含不正确的键" in msg:
                    msg = msg.replace("JSON歌词数据中包含不正确的键", self.tr("JSON歌词数据中包含不正确的键"))

                if "JSON歌词数据中包含不正确的值" in msg:
                    msg = msg.replace("JSON歌词数据中包含不正确的值", self.tr("JSON歌词数据中包含不正确的值"))

                if "不支持的歌词格式" in msg:
                    msg = msg.replace("不支持的歌词格式", self.tr("不支持的歌词格式"))

                if "无法获取歌曲标题" in msg:
                    msg = msg.replace("无法获取歌曲标题", self.tr("无法获取歌曲标题"))

                if "无法获取歌曲信息" in msg:
                    msg = msg.replace("无法获取歌曲信息", self.tr("无法获取歌曲信息"))

                if "文件格式不支持" in msg:
                    msg = msg.replace("文件格式不支持", self.tr("文件格式不支持"))

                if "获取文件信息失败" in msg:
                    msg = msg.replace("获取文件信息失败", self.tr("获取文件信息失败"))
        return msg


translator = ErrorMsgTranslator()


class LyricsRequestError():
    """歌词请求错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class LyricsProcessingError():
    """歌词处理错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class LyricsNotFoundError():
    """歌词未找到错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class LyricsDecryptError():
    """歌词解密错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class LyricsFormatError():
    """歌词格式错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class DecodingError():
    """解码错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class LyricsUnavailableError():
    """获取的歌词不可用"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)


class GetSongInfoError():
    """获取歌曲信息错误"""

    def __init__(self, msg: str) -> None:
        translator.translate(msg)
