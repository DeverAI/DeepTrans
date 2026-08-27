# -*- coding: utf-8 -*-
"""
Err.log 自动存错机制。

所有运行时错误（RE）必须被捕获并追加写入到项目根目录的 Err.log：
- 开发环境：DeepTrans/Err.log（utils/ 的上一级）
- PyInstaller 冻结后：<exe 所在目录>/Err.log

设计约束：
- 只使用标准库，绝不因记录日志本身而抛出新异常（内部全部吞掉 OSError）。
- 与 core/config.py 各自独立解析根目录，避免互相循环导入。
"""

import datetime
import os
import sys
import threading
import traceback

_LOCK = threading.Lock()


def _app_root():
    """项目根目录（开发态）或 exe 所在目录（冻结态）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    # 本文件位于 <root>/utils/ 下
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def err_log_path():
    return os.path.join(_app_root(), "Err.log")


def _append(line):
    try:
        with _LOCK:
            with open(err_log_path(), "a", encoding="utf-8") as f:
                f.write(line)
    except OSError:
        # 日志失败时放弃本次记录，绝不能再向上层抛异常。
        pass


def log_error(message):
    """追加一条错误记录（自动带时间戳）。"""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    _append("[%s] [ERROR] %s\n" % (ts, str(message).rstrip()))


def log_warning(message):
    """追加一条警告记录（例如配置校验失败、资源缺失）。"""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    _append("[%s] [WARN ] %s\n" % (ts, str(message).rstrip()))


def log_exception(context, exc=None):
    """把异常连同完整堆栈写入 Err.log。

    context: 简短说明，如 "monitor.start"、"unhandled exception"
    exc:     异常对象；为 None 时取当前线程活动异常。
    """
    if exc is None:
        exc = sys.exc_info()[1]
    if exc is None:
        log_error(str(context))
        return
    tb = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    head = "[%s] [ERROR] %s: %s: %s\n" % (
        ts, str(context).rstrip(),
        type(exc).__name__, str(exc).replace("\n", " "),
    )
    _append(head + (tb if tb.endswith("\n") or not tb else tb + "\n"))
