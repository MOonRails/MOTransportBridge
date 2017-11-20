#!/usr/local/bin/python2.7
# encoding: utf-8
'''
moonrailsbridge -- connects to the embedded software running
on a microcontroller board (i.e. Arduino) and exposes its communication
channel as a TCP/IP server

@author:     Dominik Marszk

@copyright:  2017 MO on Rails. All rights reserved.

@license:    MIT

@contact:    dmarszk@gmail.com
@deffield    updated: Updated
'''

import sys
import os
import warnings
import globalvars
import serial.tools.list_ports

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from serialtcpbridge import serialTcpBridge
from threading import Thread

__all__ = []
__version__ = 0.1
__date__ = '2017-11-19'
__updated__ = '2017-11-19'

DEBUG = 1
TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def detectArduino():
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description or 'USB-SERIAL CH340' in p.description
    ]
    if not arduino_ports:
        raise IOError("No Arduino found")
    if len(arduino_ports) > 1:
        warnings.warn('Multiple Arduinos found - using the first')
    
    ser = serial.Serial(arduino_ports[0])
    if globalvars.verbose > 0:
        print(ser)
    return ser

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Dominik Marszk on %s.
  Copyright 2017 MO on Rails. All rights reserved.

  Licensed under the MIT License
  https://opensource.org/licenses/MIT

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        globalvars.verbose = args.verbose

        if globalvars.verbose > 0:
            print("Verbose mode on")

        arduino_port = detectArduino()
        globalvars.bridge = serialTcpBridge(arduino_port)
        globalvars.bridge.runBridge()
        bridgeThread = Thread(target=globalvars.bridge.runBridge)
        bridgeThread.start()
        bridgeThread.join()
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'moonrailsbridge_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())