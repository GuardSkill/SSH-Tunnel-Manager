#!/bin/bash

echo "========================================"
echo "SSH Tunnel Manager - Linux/macOS 打包脚本"
echo "========================================"
echo ""

echo "[1/4] 检查 PyInstaller..."
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
else
    echo "PyInstaller 已安装"
fi
echo ""

echo "[2/4] 清理旧的构建文件..."
rm -rf build dist *.spec
echo "清理完成"
echo ""

echo "[3/4] 开始打包..."
pyinstaller --name="SSHTunnelManager" \
            --windowed \
            --onefile \
            --clean \
            ssh_tunnel_manager.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 打包失败！"
    exit 1
fi
echo ""

echo "[4/4] 打包完成！"
echo ""
echo "========================================"
echo "生成的可执行文件位置："
if [ "$(uname)" == "Darwin" ]; then
    echo "  dist/SSHTunnelManager.app"
else
    echo "  dist/SSHTunnelManager"
fi
echo "========================================"
echo ""

# 给可执行文件添加执行权限
if [ "$(uname)" != "Darwin" ]; then
    chmod +x dist/SSHTunnelManager
fi

echo "打包完成！"
