# DecisionHelper

一个帮助个人做决策的桌面应用。通过决策矩阵对多个选项进行加权评分，得出客观排名。

支持 macOS 和 Windows。

## 功能

- 新建、删除决策
- 为每个决策添加选项和评估标准（含权重 1–5）
- 矩阵评分界面，逐格打分（1–5 分）
- 加权总分计算与排名（评分完成后手动查看，避免锚定效应）
- 数据本地持久化（JSON）

## 安装与运行

**依赖环境：** Python 3.12，conda（推荐）

```bash
conda create -n decisionhelper python=3.12 -y
conda activate decisionhelper
pip install -r requirements.txt
python main.py
```

## 数据存储路径

| 平台    | 路径                                              |
|---------|---------------------------------------------------|
| macOS   | `~/Library/Application Support/DecisionHelper/`  |
| Windows | `%APPDATA%\DecisionHelper\`                       |

## 打包为桌面应用

```bash
pyinstaller --onedir --windowed --name DecisionHelper main.py
```

产物在 `dist/DecisionHelper.app`（macOS）或 `dist/DecisionHelper/`（Windows）。

## 评分算法

加权平均分：`sum(score × weight) / sum(weight)`，结果在 1–5 区间。

## 技术栈

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — 跨平台 GUI
- [PyInstaller](https://pyinstaller.org) — 桌面打包
