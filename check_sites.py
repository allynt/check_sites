__author__="allyn.treshansky"

"""
stand-alone script to check the status of a bunch of websites
requires a configuration file "check_sites.conf" which specifies who to email log to
requires a configuration file "check_sites.json" which defines the sites to check
note - the entries in "check_sites.json" must be completely well-formed URLs (ie: "http://google.com" as opposed to "google.com")
"""

from ConfigParser import SafeConfigParser
import os, sys, getopt, json, urllib2, smtplib

##############
# global fns #
##############

rel = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

def usage():
    """
    print usage instructions
    :return: usage string
    """
    print(u"usage: %s -f <sites file> [-v (verbose flag)]" % sys.argv[0])

#######################
# get config settings #
#######################

CONF_PATH = os.path.join(os.path.expanduser('~'), '.config', 'check_sites.conf')
parser = SafeConfigParser()
parser.read(CONF_PATH)

EMAIL_HOST = parser.get('email', 'host')
EMAIL_PORT = parser.get('email', 'port')
EMAIL_USER = parser.get('email', 'username')
EMAIL_PWD = parser.get('email', 'password')

##########################
# parse cmd-line options #
##########################

sites_file = None
verbose = False

try:
    opts, args = getopt.getopt(sys.argv[1:], 'f:v')
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-h':
        usage()
        sys.exit(2)
    elif o == '-f':
        sites_file = rel(a)
    elif o == '-v':
        verbose = True
    else:
        usage()
        sys.exit(2)

if not sites_file:
    usage()
    sys.exit(2)

############
# do stuff #
############

# get the sites to check...

with open(sites_file, "r") as f:
    sites = json.load(f)
f.closed

# check each site...

for site in sites:
    try:
        request = urllib2.urlopen(site["url"])
        code = request.code
        # if you wanted to add more logic or fine-grained detail to the log
        # here is where you would do it; using a bunch of if statments on 'code'
        site.update({
            "code": code,
            "up": True,
            "msg": "",
        })
    except Exception as e:
        site.update({
            "code": None,
            "up": False,
            "msg": e,
        })
    finally:
        request.close()

# create a log...

log = "\n".join([
    "'{0}' [{1}]: {2} ({3})".format(site["name"], site["url"], site["code"], site["msg"])
    for site in sites if not site["up"] or verbose
])

# email the log...

if log:
    mail_from = EMAIL_USER
    mail_to = EMAIL_USER
    mail_subject = "output from {0}".format(sys.argv[0])
    mail_msg = "To: {0}\nFrom: {1}\nSubject:{2}\n\n{3}".format(
        mail_from, mail_to, mail_subject, log
    )
    # have to actually login to smtp server & authenticate
    # b/c of google security
    smtpserver = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(mail_from, EMAIL_PWD)
    smtpserver.sendmail(mail_from, [mail_to], mail_msg)
    smtpserver.close()

###########
# the end #
###########
