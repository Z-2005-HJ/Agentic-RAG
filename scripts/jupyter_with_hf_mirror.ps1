# Hugging Face 国内镜像：Docling 首次运行需从 Hub 拉模型；在启动 Jupyter 前设置此脚本中的环境变量。
# Usage (PowerShell): .\scripts\jupyter_with_hf_mirror.ps1
# Optional: .\scripts\jupyter_with_hf_mirror.ps1 notebooks\week2\week2_arxiv_integration.ipynb

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$env:HF_ENDPOINT = "https://hf-mirror.com"
if (-not $env:HF_HUB_DOWNLOAD_TIMEOUT) { $env:HF_HUB_DOWNLOAD_TIMEOUT = "600" }
if (-not $env:HF_HUB_ETAG_TIMEOUT) { $env:HF_HUB_ETAG_TIMEOUT = "120" }
if (-not $env:HF_HUB_DISABLE_SYMLINKS_WARNING) { $env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1" }
# 可选：固定缓存目录
if (-not $env:HF_HOME) {
    $env:HF_HOME = Join-Path $env:USERPROFILE ".cache\huggingface"
}

Write-Host "HF_ENDPOINT=$env:HF_ENDPOINT"
Write-Host "HF_HUB_DOWNLOAD_TIMEOUT=$env:HF_HUB_DOWNLOAD_TIMEOUT"
Write-Host "HF_HOME=$env:HF_HOME"
Write-Host "Project: $ProjectRoot"
Write-Host ""

$notebook = $args[0]
if (-not $notebook) {
    $notebook = "notebooks\week2\week2_arxiv_integration.ipynb"
}

Write-Host "Starting: uv run jupyter notebook $notebook"
& uv run jupyter notebook $notebook
