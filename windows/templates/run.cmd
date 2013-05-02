@echo off

SET CMDLINE=%*

SET ENV_DRIVE=%~d0%
SET ENV_PATH=%~p0%
SET ENV=%ENV_DRIVE%%ENV_PATH%

SET PATH=%ENV%\\python\\;%ENV%\\python\\Scripts;%PATH%
SET PYTHONPATH=%ENV%\\python\\Lib
SET PYTHONUNBUFFERED=1

SET HOME=%CD%

IF %1!==! goto interactive
  REM MSYS cannot handle backslashes. So we have to replace all of them with slashes
  %ENV%\\msys\\bin\\bash --login -c '%CMDLINE:\=/%'
  goto end

:interactive
start %ENV%\\msys\\bin\\mintty /bin/bash -l

:end
