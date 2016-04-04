# check_sites
simple python script for checking whether websites are up

uses 2 simple configuration files:
* "check_sites.conf": specifies the email settings to be used
* "check_sites.json": specifies the sites to check

takes 2 arguments:
* -f <file>: specifices the path to "check_sites.json"
* -v: specifies "verbose" mode (in non-verbose mode, an email is only sent if any sites DO NOT return a status code of 200)

best used w/ cron to check a set of websites automatically
