# 人口通 - 桌面端（Windows 客户端）

人口通系统的桌面端仓库（PyQt6 客户端），连接服务端使用，支持本地/网络双模式。

> 本仓库由原 `db-population-system` 拆分而来；服务端与 Web 前端在 `db-population-system-server`，移动端在 `db-population-system-mobile`。

## 功能

### 人员 / 家庭管理

- 人员新增、编辑、删除 / 恢复、分户合户
- **每户唯一户主**：添加成员关系为"户主"时自动校验，已有户主则拒绝
- **换户主整户关系重建**：把某人改为"户主"，系统自动重算全户成员与新户主的关系——旧户主变父/母、配偶变父/母、其他子女按年龄自动变兄/弟/姐/妹、旧户主父母变祖父/祖母等；无法确定归属的（孙辈、儿媳）保持原值不强行改错
- **与户主关系标准下拉**：依据公安部户口簿规范 + GB 4761-1984 家庭关系代码 + 民法典近亲属，提供 45 项标准关系（户主/配偶/子女/父母/祖父母/兄弟姐妹/儿媳女婿等），同时支持自定义输入
- 家庭视图：查看同户成员，添加家庭成员自动带出同户地址与小组
- "小组"字段（与地址配套，同户一致）

### Excel 批量导入 / 导出

- 人口信息导入模板（支持数据库全部字段：身份证号、小组、残疾类型、社保卡等）
- 补贴导入模板：低保、特困、残疾人护理补贴、高龄补贴、养老保险、地力补贴
- 报表填写与一键导入证件号码

### 补贴数据管理

- 地力补贴、养老保险、低保、特困、残疾人护理补贴、高龄补贴
- 社保卡 1/2/3 号管理，2/3 号卡由补贴导入自动回填来源；同一人存在多个不同社保卡时展示最多 3 个，每个卡标注来源

### 其他功能

- 数据统计、报表导出（可按残疾等级等条件筛选）
- 年级晋升、照片管理、数据备份
- 操作日志（在线模式记录到服务端）
- **自动更新**：检查更新（服务器主源 + SHA256 强校验）→ 下载 → 立即更新重启 / 暂不更新

### 运行模式

- **本地模式**：SQLite 单机使用
- **网络模式**：连接服务端（HTTPS + 证书固定），记录上次服务器地址，二次打开自动填入

## 运行

```bash
# 本地模式
./start_desktop.sh local

# 网络模式（连服务端）
./start_desktop.sh network https://服务器IP:5000
```

Windows 下开发运行：

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements_desktop.txt
.\venv\Scripts\python main.py
```

## 打包（Windows 安装程序 exe）

```bash
pip install -r requirements_desktop.txt pyinstaller
pyinstaller --noconfirm 人口通.spec     # 生成 dist\人口通\
```

再用 Inno Setup 6 编译 `人口通_installer.iss` 生成一键安装 exe（安装包含证书固定所需的客户端证书）。

## 目录结构

```
main.py               # 入口（MainWindow 骨架，方法绑定自 ui/main_window/）
ui/main_window/       # MainWindow 方法，一方法一文件
dialogs/              # 各业务对话框（人员编辑/添加、补贴等）
core/                 # 数据库（模型一文件一表）、配置、工具
data/                 # Excel 导入器 / 模板生成
network/              # 网络模式客户端（API 封装）
updates/version.json  # 内置版本号（打包读取）
certs/                # 客户端 SSL 证书（证书固定）
```

## 数据库

- 本地库：`core/population.db`（启动自动迁移）
- 备份：`core/data/backups/`（自动 + 手动）
