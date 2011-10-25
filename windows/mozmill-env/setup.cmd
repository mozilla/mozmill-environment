@echo off

SET MOZMILLDRIVE=%~d0%
SET MOZMILLPATH=%~p0%
SET MOZMILL=%MOZMILLDRIVE%%MOZMILLPATH%

SET PATH=%PATH%;%MOZMILL%\python26\;%MOZMILL%\python26\Scripts

rem Update installation paths
easy_install --upgrade pip

rem Install packages
pip install --upgrade mozmill
