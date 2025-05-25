"""
pytestを使ったテストのサンプル。
このファイルは、pytestの基本的な使い方を示します。
"""
import pytest

def add(a, b):
    """
    2つの数値を加算して返すサンプル関数。
    """
    return a + b

def test_add():
    """
    add関数が正しく加算できるかのテスト。
    """
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_add_typeerror():
    """
    add関数に数値以外を渡した場合にTypeErrorが発生することを確認。
    """
    with pytest.raises(TypeError):
        add('a', 1)
