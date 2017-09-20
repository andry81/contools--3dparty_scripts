@echo off

setlocal

(
  echo.[LocalPath]
  echo.3dparty_root = d:\3dparty
  echo.tests_data_root = d:\tests_data
) > "%~dp0_env.ini"
