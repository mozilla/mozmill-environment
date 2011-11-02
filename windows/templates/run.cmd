@echo off

SET ENV_DRIVE=%~d0%
SET ENV_PATH=%~p0%
SET ENV=%ENV_DRIVE%%ENV_PATH%
SET SHELL=%ENV%\\msys\\bin\\bash --login

SET PATH=%PATH%;%ENV%\\python\\;%ENV%\\python\\Scripts
SET PYTHONPATH=%ENV%\\python\\Lib

SET HOME=%ENV%

IF %1!==! goto interactive
%SHELL% -c "%*"
goto end

:interactive
echo "Welcome to Mozmill. Use 'mozmill --help' for assistance.
start "" %SHELL% -i

:end
