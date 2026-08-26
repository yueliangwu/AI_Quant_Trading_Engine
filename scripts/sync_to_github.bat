@echo off
rem ST项目 -> GitHub 同步（Windows 便捷入口）
rem 如需指定受管 python，把下面的 python 换成绝对路径，例如：
rem "C:\Users\EDY\.workbuddy\binaries\python\versions\3.13.12\python.exe" "%~dp0sync_to_github.py" %*
python "%~dp0sync_to_github.py" %*
