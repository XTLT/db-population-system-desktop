#!/bin/bash
# ========================================
# 人口通 - 桌面端启动脚本
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="${SCRIPT_DIR}/desktop"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo_error "未找到 Python3，请先安装 Python3"
        exit 1
    fi
}

# 安装桌面端依赖
install_dependencies() {
    echo_info "安装桌面端依赖..."
    cd "${DESKTOP_DIR}"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r ../requirements_desktop.txt
    
    echo_info "桌面端依赖安装完成"
}

# 启动桌面端
start_desktop() {
    local MODE=${1:-"local"}  # local 或 network
    local SERVER_URL=${2:-""}
    
    cd "${DESKTOP_DIR}"
    
    if [ ! -d "venv" ]; then
        install_dependencies
    fi
    
    source venv/bin/activate
    
    echo_info "启动桌面端客户端..."
    echo ""
    echo "========================================"
    echo "   人口通 - 桌面端"
    echo "========================================"
    if [ "$MODE" = "network" ]; then
        echo "  模式: 网络模式"
        echo "  服务器: ${SERVER_URL}"
    else
        echo "  模式: 本地模式"
        echo "  数据库: 本地 SQLite"
    fi
    echo "========================================"
    echo ""
    
    # 设置环境变量
    export POPULATION_SERVER_URL="${SERVER_URL}"
    export POPULATION_MODE="${MODE}"

    # SSH 远程运行时无图形环境：自动探测本机图形会话（如本机已登录桌面）
    if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
        local ACTIVE_SESSION ACTIVE_UID XAUTH_FILE
        ACTIVE_SESSION=$(loginctl list-sessions --no-legend 2>/dev/null | awk '$4=="seat0" && $6=="active"{print $1; exit}')
        if [ -n "$ACTIVE_SESSION" ]; then
            ACTIVE_UID=$(loginctl show-session "$ACTIVE_SESSION" -p User --value 2>/dev/null)
            if [ -n "$ACTIVE_UID" ]; then
                export XDG_RUNTIME_DIR="/run/user/${ACTIVE_UID}"
                # 优先使用 Wayland 会话的 Xwayland 授权文件
                XAUTH_FILE=$(ls "${XDG_RUNTIME_DIR}"/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
                if [ -z "$XAUTH_FILE" ] && [ -f "${HOME}/.Xauthority" ]; then
                    XAUTH_FILE="${HOME}/.Xauthority"
                fi
                if [ -n "$XAUTH_FILE" ]; then
                    export DISPLAY=:0
                    export XAUTHORITY="$XAUTH_FILE"
                    echo_info "检测到本机图形会话（session ${ACTIVE_SESSION}），自动设置 DISPLAY=:0"
                fi
            fi
        fi
        if [ -z "${DISPLAY:-}" ]; then
            echo_warn "未检测到可用图形环境，请在桌面环境终端中运行，或检查本机是否已登录图形会话"
        fi
    fi

    python3 main.py
}

# 使用帮助
show_help() {
    echo "人口通 - 桌面端管理脚本"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  start [mode] [server_url]  启动桌面端"
    echo "                             mode: local(默认) 或 network"
    echo "                             server_url: 网络模式时的服务器地址"
    echo "  install                    安装依赖"
    echo "  help                       显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 start local                           # 本地模式"
    echo "  $0 start network https://192.168.1.100:5000  # 网络模式"
}

# 主入口
case "${1:-help}" in
    start)
        start_desktop "${2:-local}" "${3:-}"
        ;;
    install)
        check_python
        install_dependencies
        ;;
    help|*)
        show_help
        ;;
esac
