@echo off
title Suggu Services Super Admin E2E Test Suite
cd /d "%~dp0"
echo ===========================================================================
echo   STARTING SUGGU SERVICES SUPER ADMIN FULL-SCREEN CHROME E2E TESTS
echo ===========================================================================
.\env\Scripts\python.exe -u test_super_admin_e2e.py
pause
