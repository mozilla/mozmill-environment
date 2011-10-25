Test environment for Mozmill test execution via the command line on Linux.

Note: Configure the environment before the first use by running setup.sh. The
      script depends on the python-dev package, which has to be installed first.


Usage
====
The start script can be used manually or scripted. For the latter mode,
parameters have to be passed in. The maximum number of allowed
parameters is 9.

Manual:   run.sh
Scripted: run.sh mozmill -b /usr/bin/firefox-bin -t ~/mozmill-tests/firefox
