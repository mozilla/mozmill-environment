@echo off

SET MOZMILLDRIVE=%~d0%
SET MOZMILLPATH=%~p0%
SET MOZMILL=%MOZMILLDRIVE%%MOZMILLPATH%

SET PATH=%PATH%;%MOZMILL%\python26\;%MOZMILL%\python26\Scripts

echo "Welcome to Mozmill. Use 'mozmill --help' for assistance.
%*
