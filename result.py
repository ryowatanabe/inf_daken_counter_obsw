from datetime import datetime
from logging import getLogger

logger_child_name = 'result'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded result.py')

results_dirname = 'results'
filtereds_dirname = 'filtered'

"""
result.py

このスクリプトは、ゲームの結果情報を管理するためのものです。

主な機能:
- プレイ情報、スコア、オプション設定などの結果データを格納
- 新しい記録があるかどうかの判定
"""

class ResultInformations():
    """
    プレイ情報を格納するクラス。

    属性:
    - play_mode: プレイモード (str)
    - difficulty: 難易度 (str)
    - level: レベル (str)
    - notes: ノーツ数 (int)
    - music: 音楽名 (str)
    """
    def __init__(self, play_mode: str, difficulty: str, level: str, notes: int, music: str):
        self.play_mode = play_mode
        self.difficulty = difficulty
        self.level = level
        self.notes = notes
        self.music = music

class ResultValues():
    """
    スコアやクリアタイプなどの値を格納するクラス。

    属性:
    - best: ベストスコアまたは値 (str | int)
    - current: 現在のスコアまたは値 (str | int)
    - new: 新しい記録かどうか (bool)
    """
    def __init__(self, best: str | int, current: str | int, new: bool):
        self.best = best
        self.current = current
        self.new = new

class ResultOptions():
    """
    プレイ時のオプション設定を格納するクラス。

    属性:
    - arrange: アレンジ設定 (str)
    - flip: フリップ設定 (str)
    - assist: アシスト設定 (str)
    - battle: バトルモードかどうか (bool)
    - special: 特殊設定かどうか (bool)
    """
    def __init__(self, arrange: str, flip: str, assist: str, battle: bool):
        self.arrange = arrange
        self.flip = flip
        self.assist = assist
        self.battle = battle
        self.special = (arrange is not None and 'H-RAN' in arrange) or self.battle

class ResultDetails():
    """
    詳細な結果情報を格納するクラス。

    属性:
    - graphtype: グラフの種類 (str)
    - options: オプション設定 (ResultOptions)
    - clear_type: クリアタイプ (ResultValues)
    - dj_level: DJ レベル (ResultValues)
    - score: スコア (ResultValues)
    - miss_count: ミスカウント (ResultValues)
    - graphtarget: グラフターゲット (str)
    """
    def __init__(self, graphtype: str, options: ResultOptions, clear_type: ResultValues, dj_level: ResultValues, score: ResultValues, miss_count: ResultValues, graphtarget: str):
        self.graphtype = graphtype
        self.options = options
        self.clear_type = clear_type
        self.dj_level = dj_level
        self.score = score
        self.miss_count = miss_count
        self.graphtarget = graphtarget

class Result():
    """
    ゲームの結果全体を格納するクラス。

    属性:
    - informations: プレイ情報 (ResultInformations)
    - play_side: プレイサイド (str)
    - rival: ライバルモードかどうか (bool)
    - dead: デッド状態かどうか (bool)
    - details: 詳細な結果情報 (ResultDetails)
    - timestamp: タイムスタンプ (str)
    """
    def __init__(self, informations: ResultInformations, play_side: str, rival: bool, dead: bool, details: ResultDetails):
        self.informations: ResultInformations = informations
        self.play_side = play_side
        self.rival = rival
        self.dead = dead
        self.details: ResultDetails = details

        now = datetime.now()
        self.timestamp = f"{now.strftime('%Y%m%d-%H%M%S')}"
    
    def has_new_record(self):
        """
        新しい記録があるかどうかを判定します。

        戻り値:
        - 新しい記録がある場合は True、それ以外は False
        """
        return any([
            self.details.clear_type is not None and self.details.clear_type.new,
            self.details.dj_level is not None and self.details.dj_level.new,
            self.details.score is not None and self.details.score.new,
            self.details.miss_count is not None and self.details.miss_count.new
        ])

