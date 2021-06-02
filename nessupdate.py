#!/usr/bin/env python3


import argparse
import os
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
                        action='store', dest='license')
    return parser

def windows(args):
    """Updates a Nessus installation on a Windows operating system"""
    try:
        subprocess.check_call(shlex.split('cd c:\Program Files\Tenable\Nessus'))
        subprocess.check_call(shlex.split('net stop "Tenable Nessus"'))
        p = subprocess.Popen(shlex.split('nessuscli.exe fix --reset'),
                             stdin=subprocess.PIPE)
        p.communicate(input=b'y\n')
        rCode = None
        while rCode == None:
            rCode = p.poll()
        if rCode != 0:
            raise subprocess.CalledProcessError("Command 'nessuscli.exe fix " +
                                                "--reset' returned non-zero " +
                                                "exit status " + str(rCode))
        if args.proxyAddr and args.proxyPort:
            try:
                subprocess.check_call(shlex.split('nessuscli.exe fetch ' + 
                                                  '--register ' + args.license))
            except:
                pass
            subprocess.check_call(shlex.split('nessuscli.exe fix --secure ' +
                                              '--set proxy=' + args.proxyAddr))
            subprocess.check_call(shlex.split('nessuscli.exe fix --secure ' +
                                              '--set proxy_port=' + 
                                              str(args.proxyPort)))
            if args.proxyUser and args.proxyPass:
                subprocess.check_call(shlex.split('nessuscli.exe fix --secure' +
                                                  ' --set proxy_username=' +
                                                  args.proxyUser))
                subprocess.check_call(shlex.split('nessuscli.exe fix --secure' +
                                                  ' --set proxy_password=' +
                                                  args.proxyPass))
            else:
                sys.exit("Please provide both a username and password to use " +
                         "an authenticated proxy")
        else:
            sys.exit("Please provide both an IP address/hostname and port " +
                     "number to use a proxy")
        subprocess.check_call(shlex.split('nessuscli.exe fetch --register ' + 
                                          args.license))
        subprocess.check_call(shlex.split('nessuscli.exe update --all'))
        if args.rebuild:
            subprocess.check_call(shlex.split('nessusd -R'))
        subprocess.check_call(shlex.split('net start "Tenable Nessus"'))
    except Exception as e:
        sys.exit("Failed to update Nessus:\n" + str(e))

def nix(args):
    """Updates a Nessus installation on a *nix operating system"""
    svcCmd = ""
    if 
    #TODO
    # Linux (Root permissions)
    #     # cd /opt/nessus/sbin
    #     # service nessusd stop
    #     # ./nessuscli fix --reset (select "y" ; this command only clears the SMTP and proxy settings. It will not touch any scans or scan history.)
    #     If you have a proxy follow the below steps
    #     # ./nessuscli fetch --register <activationcode> (this will error out; continue with setting the proxy)
    #     # ./nessuscli fix --secure --set proxy=<ip/hostname>
    #     # ./nessuscli fix --secure --set proxy_port=<port>
    #     # ./nessuscli fix --secure --set proxy_username=<user>
    #     # ./nessuscli fix --secure --set proxy_password=<password>
    #     Continue here
    #     # ./nessuscli fetch --register <activationcode>
    #     # ./nessuscli update --all
    #     # ./nessusd -R (optional command to rebuild the plugin database)
    #     # service nessusd start
    pass 

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
    parser = genParser() 
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        getOsFunc()(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Killed by user")
