#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ST项目 -> GitHub 同步脚本（跨平台）

功能：将当前项目全部变更暂存 -> 提交(带日期) -> 推送到 origin/main。
用法：
    python scripts/sync_to_github.py                # 默认日期提交信息
    python scripts/sync_to_github.py --msg "手动说明" # 自定义提交信息
依赖：仅标准库；需已配置好 git 且 origin 指向可写仓库。
"""
import subprocess
import sys
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    print("[sync]", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode


def main():
    msg = "sync: " + datetime.date.today().isoformat() + " 自动同步项目状态与ST分析产出"
    if "--msg" in sys.argv:
        idx = sys.argv.index("--msg")
        if idx + 1 < len(sys.argv):
            msg = sys.argv[idx + 1]

    if run(["git", "add", "-A"]) != 0:
        sys.exit(1)

    # 无暂存变更则跳过提交
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if r.returncode == 0:
        print("[sync] 无变更，跳过提交。")
        return

    if run(["git", "commit", "-m", msg]) != 0:
        sys.exit(1)
    if run(["git", "push", "origin", "main"]) != 0:
        sys.exit(1)
    print("[sync] 完成：已推送到 origin/main @", datetime.date.today().isoformat())


if __name__ == "__main__":
    main()
