#!/usr/bin/env python3


"""Script to update a nessus installation. Based on instructions found at
https://community.tenable.com/s/article/Receiving-Installation-Expired-When-Attempting-to-Login-to-Nessus
"""


import argparse
import os
import ctypes
import shlex
import subprocess
import sys


def genParser():
    """Generates a CLI argument parser"""
    parser = argparse.ArgumentParser(description="A utility to update a " +
                                     "Nessus instalation")
    parser.add_argument('-n', '--no-rebuild', help="do not rebuild the " +
                        "plugin database", action='store_false', dest='rebuild')
    parser.add_argument('-pA', '--proxy-addr', help="IP address or hostname " +
                        "for the proxy", type=str, action='store',
                        dest='proxyAddr')
    parser.add_argument('-pP', '--proxy-port', help="port number for the proxy",
                        type=int, action='store', dest='proxyPort')
    parser.add_argument('-pU', '--proxy-user', help="username for the proxy",
                        type=str, action='store', dest='proxyUser')
    parser.add_argument('-pC', '--proxy-pass', help="password for the proxy",
                        type=str, action='store', dest='proxyPass')
    parser.add_argument('license', help="Nessus license code", type=str,
                        action='store')
    return parser

def windows(args):
    """Updates a Nessus installation on a Windows operating system"""
    nDir = "C:\\Program Files\\Tenable\\Nessus"
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        sys.exit("Administrator privileges required (try rerunning in an " +
                 "administrator command prompt)")
    try:
        os.chdir(nDir)
    except KeyboardInterrupt:
        sys.exit("Killed by user")
    except:
        sys.exit("Nessus does not appear to be installed")
    p = subprocess.Popen(shlex.split('net stop "Tenable Nessus"'),
                                     stderr=subprocess.PIPE)
    rCode = None
    while rCode == None:
        rCode = p.poll()
    err = p.stderr.readline().rstrip()
    if err not in [b'The Tenable Nessus service is not started.', 
                   b'The Tenable Nessus service was stopped successfully.']:
        sys.exit("Could not stop the Tenable Nessus service")
    try:
        p = subprocess.Popen([nDir + '\\nessuscli.exe', 'fix', '--reset'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        p.stdout.readline()
        p.stdout.readline()
        p.communicate(input=b'y\r\n') #This is broken
        rCode = None
        while rCode == None:
            rCode = p.poll()
        if rCode != 0:
            raise Exception("Command 'nessuscli.exe fix " +
                                                "--reset' returned non-zero " +
                                                "exit status " + str(rCode))
        if args.proxyAddr and args.proxyPort:
            try:
                subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe ' + 
                                                  'fetch --register ' + 
                                                  args.license))
            except KeyboardInterrupt:
                sys.exit("Killed by user")
            except:
                pass
            subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe fix ' +
                                              '--secure --set proxy=' + 
                                              args.proxyAddr))
            subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe fix' +
                                              ' --secure --set proxy_port=' + 
                                              str(args.proxyPort)))
            if args.proxyUser and args.proxyPass:
                subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe fix' +
                                                  ' --secure --set ' +
                                                  'proxy_username=' +
                                                  args.proxyUser))
                subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe fix' +
                                                  ' --secure --set ' +
                                                  'proxy_password=' +
                                                  args.proxyPass))
            else:
                if args.proxyUser or args.proxyPass:
                    sys.exit("Please provide both a username and password to " +
                             "use an authenticated proxy")
        else:
            if args.proxyAddr or args.proxyPort:
                sys.exit("Please provide both an IP address/hostname and port" +
                         " number to use a proxy")
        subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe fetch ' + 
                                          '--register ' + args.license))
        subprocess.check_call(shlex.split(nDir + '\\nessuscli.exe update --all')
                                         )
        if args.rebuild:
            subprocess.check_call(shlex.split(nDir + '\\nessusd.exe -R'))
        subprocess.check_call(shlex.split('net start "Tenable Nessus"'))
        print("Nessus updated successfully")
    except KeyboardInterrupt:
        sys.exit("Killed by user")
#    except:
#        sys.exit("Failed to update Nessus")

def nix(args):
    """Updates a Nessus installation on a *nix operating system"""
    if os.geteuid() != 0:
        sys.exit("Root privileges required (try rerunning using sudo)")
    svcRstCmd = ""
    try:
        os.chdir('/opt/nessus/sbin')
    except KeyboardInterrupt:
        sys.exit("Killed by user")
    except:
        sys.exit("Nessus does not appear to be installed")
    try:
        subprocess.check_call(shlex.split('systemctl stop nessusd'))
        svcRstCmd = "systemctl start nessusd"
    except:
        try:
            subprocess.check_call(shlex.split('service nessusd stop'))
            svcRstCmd = "service nessusd start"
        except KeyboardInterrupt:
            sys.exit("Killed by user")
        except:
            sys.exit("Could not stop nessusd service")
    try:
        p = subprocess.Popen(shlex.split('./nessuscli fix --reset'),
                             stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
        p.communicate(input=b'y\n')
        rCode = None
        while rCode == None:
            rCode = p.poll()
        if rCode != 0:
            raise subprocess.CalledProcessError("Command './nessuscli fix " +
                                                "--reset' returned non-zero " +
                                                "exit status " + str(rCode))
        if args.proxyAddr and args.proxyPort:
            try:
                subprocess.check_call(shlex.split('./nessuscli fetch ' + 
                                                  '--register ' + args.license))
            except KeyboardInterrupt:
                sys.exit("Killed by user")
            except:
                pass
            subprocess.check_call(shlex.split('./nessuscli fix --secure ' +
                                            '--set proxy=' + args.proxyAddr))
            subprocess.check_call(shlex.split('./nessuscli fix --secure ' +
                                            '--set proxy_port=' + 
                                            str(args.proxyPort)))
            if args.proxyUser and args.proxyPass:
                subprocess.check_call(shlex.split('./nessuscli fix --secure' +
                                                  ' --set proxy_username=' +
                                                  args.proxyUser))
                subprocess.check_call(shlex.split('./nessuscli fix --secure' +
                                                  ' --set proxy_password=' +
                                                  args.proxyPass))
            else:
                if args.proxyUser or args.proxyPass:
                    sys.exit("Please provide both a username and password to " +
                             "use an authenticated proxy")
        else:
            if args.proxyAddr or args.proxyPort:
                sys.exit("Please provide both an IP address/hostname and port" +
                         " number to use a proxy")
        subprocess.check_call(shlex.split('./nessuscli fetch --register ' + 
                                          args.license))
        subprocess.check_call(shlex.split('./nessuscli update --all'))
        if args.rebuild:
            subprocess.check_call(shlex.split('./nessusd -R'))
        subprocess.check_call(shlex.split(svcRstCmd))
        print("Nessus updated successfully")
    except KeyboardInterrupt:
        sys.exit("Killed by user")
    except:
        sys.exit("Failed to update Nessus")

def getOsFunc():
    """Returns an appropriate function based on the operating system"""
    if os.name == "nt":
        return windows
    if os.name == "posix":
        return nix
    else:
        sys.exit("This operating system is not supported")

def main():
    """Main method"""
    try:
        parser = genParser() 
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            getOsFunc()(args)
    except KeyboardInterrupt:
        sys.exit("Killed by user")


if __name__ == "__main__":
    main()
