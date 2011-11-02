Test environment for Mozmill test execution via the command line on Windows.

Note: Configure the environment before the first use by running setup.cmd.


Usage
====
The start script can be used manually or scripted. For the latter mode,
parameters have to be passed in. The maximum number of allowed
parameters is 9.

Manual:   run.cmd
Scripted: run.cmd mozmill -b c:\firefox\firefox.exe -t c:\mozmill-tests\firefox
