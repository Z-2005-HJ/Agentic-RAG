# Bilingual comments policy / 双语注释策略：保留英文；中文为补充释义。

"""
Simple launcher for the Gradio interface.
Run this script to start the web UI for the arXiv Paper Curator RAG system.

中文：Gradio 界面启动入口脚本；运行后即可在浏览器访问本地聊天 UI（默认端口见 `gradio_launcher`/`gradio_app` 配置）。
"""

import sys
from pathlib import Path

# Add src to Python path  # 将 src 加入 Python 路径，便于 `import src...`
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.gradio_app import main

if __name__ == "__main__":
    main()
