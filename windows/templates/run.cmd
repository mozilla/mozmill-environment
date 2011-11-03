@echo off

SET ENV_DRIVE=%~d0%
SET ENV_PATH=%~p0%
SET ENV=%ENV_DRIVE%%ENV_PATH%

SET PATH=%PATH%;%ENV%\\python\\;%ENV%\\python\\Scripts
SET PYTHONPATH=%ENV%\\python\\Lib

SET HOME=%ENV%

IF %1!==! goto interactive
  %ENV%\\msys\\bin\\bash --login -c "%*"
  goto end

:interactive
start %ENV%\\msys\\bin\\mintty /bin/bash -l

:end
