@echo off
cd /d "%~dp0"
start "" "http://localhost:8742/worldcup-2026-live.html"
python serve.py
