#!/usr/bin/python

# Elevate permissions
import os
import sys
import getopt
import drivers
import string
import functions
import gtk
import gettext
from logger import Logger
from dialogs import MessageDialogSave

# i18n
gettext.install("ddm", "/usr/share/locale")


# Help
def usage():
    # Show usage
    hwOpt = ''
    for hw in drivers.hwCodes:
        if hwOpt != '':
            hwOpt += ', '
        hwOpt += hw
    hlp = """ddm [options]

Options:
  -c (--codes): comma separated list with pre-selected hardware
                possible hardware codes: %s
  -d (--debug): print debug information to a log file in user directory
  -f (--force): force start in a live environment
  -h (--help): show this help
  -i (--install): install preselected hardware drivers (see codes)"""
    print hlp % (hwOpt)

# Handle arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hic:df', ['help', 'install', 'codes=', 'debug', 'force'])
except getopt.GetoptError:
    usage()
    sys.exit(2)

debug = False
force = False
for opt, arg in opts:
    if opt in ('-d', '--debug'):
        debug = True
    elif opt in ('-f', '--force'):
        force = True
    elif opt in ('-h', '--help'):
        usage()
        sys.exit()


# Initialize logging
logFile = ''
if debug:
    logFile = 'ddm.log'
log = Logger(logFile)
functions.log = log
if debug:
    if os.path.isfile(log.logPath):
        open(log.logPath, 'w').close()
    log.write(_("Write debug information to file: %(path)s") % { "path": log.logPath }, 'main', 'info')

# Log some basic environmental information
machineInfo = functions.getSystemVersionInfo()
log.write(_("Machine info: %(info)s") % { "info": machineInfo }, 'main', 'info')
version = functions.getPackageVersion('ddm')
log.write(_("DDM version: %(version)s") % { "version": version }, 'main', 'info')

# There were issues with apt-listbugs
# Warn the user for any errors that might accur when apt-listbugs is installed
if functions.isPackageInstalled('apt-listbugs'):
    log.write(_("apt-listbugs is installed and might interfere with driver installation"), 'main', 'warning')

# Set variables
scriptDir = os.path.dirname(os.path.realpath(__file__))

# Pass arguments to ddm.py: replace - with : -> because kdesudo assumes these options are meant for him...
# TODO: Isn't there another way?
args = ' '.join(sys.argv[1:])
if len(args) > 0:
    args = ' ' + string.replace(args, '-', ':')
    # Pass the log path to ddm.py
    if debug:
        args += ' :l ' + log.logPath

if functions.hasInternetConnection() or force:
    if not functions.getDistribution() == '' or force:
        # Do not run in live environment
        if not functions.isRunningLive() or force:
            ddmPath = os.path.join(scriptDir, 'ddm.py' + args)

            # Add launcher string, only when not root
            launcher = ''
            if os.geteuid() > 0:
                launcher = "gksu --message \"<b>%s</b>\"" % _("Please enter your password")
                if os.path.exists('/usr/bin/kdesudo'):
                    launcher = "kdesudo -i /usr/share/ddm/logo.png -d --comment \"<b>%s</b>\"" % _("Please enter your password")

            cmd = '%s python %s' % (launcher, ddmPath)
            log.write(_("Startup command: %(cmd)s") % { "cmd": cmd }, 'main', 'debug')
            os.system(cmd)
        else:
            title = _("DDM - Live environment")
            msg = _("DDM cannot run in a live environment\n\nTo force start, use the --force argument")
            MessageDialogSave(title, msg, gtk.MESSAGE_INFO).show()
            log.write(msg, 'main', 'warning')
    else:
        title = _("DDM - Debian based")
        msg = _("Cannot determine the base distribution (debian or ubuntu)\n\nTo force start, use the --force argument")
        MessageDialogSave(title, msg, gtk.MESSAGE_INFO).show()
        log.write(msg, 'main', 'warning')
else:
    title = _("DDM - Internet")
    msg = _("You do not seem to have an internet connection\n\nTo force start, use the --force argument")
    MessageDialogSave(title, msg, gtk.MESSAGE_INFO).show()
    log.write(msg, 'main', 'warning')