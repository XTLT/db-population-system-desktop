# 人口通 - 桌面端

人口通系统的桌面端仓库（PyQt6 客户端）。

> 本仓库由原 `db-population-system` 拆分而来，仅包含桌面端；服务端与 Web 前端在 `db-population-system-server`，移动端在 `db-population-system-mobile`。

## 功能

- 人员/家庭管理（新增、编辑、删除、恢复、分户合户）
- Excel 批量导入导出（人员、学生就读、林地、各补贴）
- 补贴数据管理（地力补贴、养老保险、低保、特困、残疾人护理补贴、高龄补贴）
- 社保卡 1/2/3 管理（2/3 号卡由补贴导入自动回填来源）
- 年级晋升、照片管理、数据备份、更新检查、操作日志
- 本地模式（SQLite）与网络模式（连服务端）双模式

## 运行

```bash
# 本地模式
./start_desktop.sh local

# 网络模式（连服务端）
./start_desktop.sh network https://服务器IP:5000
```

Windows 下：

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements_desktop.txt
.\venv\Scripts\python main.py
```

## 打包

Windows 一键打包（GitHub Actions 已配置，push 后自动构建并发布到 Releases，保留最新 2 版）：

```bash
pip install -r requirements_desktop.txt pyinstaller
cd desktop
pyinstaller --noconfirm 人口通.spec
```

## 目录结构

```
main.py               # 入口（MainWindow 骨架，方法绑定自 ui/main_window/）
ui/main_window/       # MainWindow 的 59 个方法，一方法一文件
dialogs/              # 各业务对话框
core/                 # 数据库（模型一文件一表）、配置、工具
data/                 # Excel 导入器/模板生成（不入库）
network/              # 网络模式客户端
updates/version.json  # 版本号（CI 打包读取）
certs/                # 网络模式 SSL 证书
```

## 数据库

- 本地库：`core/population.db`（启动自动迁移）
- 备份：`core/data/backups/`（自动 + 手动）
