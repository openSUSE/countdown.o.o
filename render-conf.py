#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Release countdown banner generation script
# by Pascal Bleser <pascal.bleser@opensuse.org>
# Artwork by jimmac
#

import sys
import datetime
import fileinput
from optparse import OptionParser
import os
import subprocess
import tempfile
import shutil
import atexit

#VERSION = 2011
RELEASE_BEGIN = datetime.datetime(2018, 05, 26, 12, 0, 0)
RELEASE_END = datetime.datetime(2018, 05, 26, 0, 0)
VERSION = RELEASE_BEGIN.year

# dimensions are tuples of (width,height,name)
#sizes = [(600,105,"wide"), (400,400,"large"), (256,256,"medium"), (130,130,"small")]
sizes = [(400,400,"large"), (256,256,"medium"), (130,130,"small")]
variants = [ '' ] #, '-terminal' ]

options = None
optionParser = OptionParser(usage="%prog [options] [<output directory>]",
        description="render countdown image")
optionParser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
        help='be verbose')
(options, args) = optionParser.parse_args(sys.argv)

if len(args) >= 2:
    prefix = args[1]
else:
    prefix = "../output/conf/%s" % VERSION
    pass

nao = datetime.datetime.now()

diff_begin = (RELEASE_BEGIN - nao)
diff_end = (nao - RELEASE_END)

if diff_end.days >= 1:
    days = -1
else:
    days = diff_begin.days
    pass
color = (255, 255, 255, 255)

workdir = None

def on_exit():
    if workdir != None and os.path.exists(workdir):
        shutil.rmtree(workdir)
        pass
    pass
atexit.register(on_exit)

workdir = tempfile.mkdtemp(prefix='countdown', suffix='tmp')

if not os.path.exists(prefix):
    print "Created output directory %s" % prefix
    os.makedirs(prefix)
    pass

def render(d, variant):
    if d >= 1:
        days = "%d" % d
        ext = ""
    elif d < 0:
        days = None
        ext = "-done"
    else:
        days = None
        ext = "-outnow"
        pass

    for size in sizes:
        template = "osconf%s%s%s.svg" % (VERSION, variant, ext)
        workfile = os.path.join(workdir, "work.svg")
        out = open(workfile, "wb")
        for line in fileinput.FileInput(template, mode="rb"):
            #line = unicode(line)
            if days != None:
                line = line.replace("@@", days)
                pass
            out.write(line)
            pass
        out.close()
        outfile = "%s/%s%s.png" % (prefix, size[2], variant)

        #inkscape --export-png=foo.png --export-area-page -w 400 -h 400 osconf10_.svg
        rc = subprocess.call(["inkscape", "-z", "--export-png=%s" % outfile, "--export-area-page", "-w", str(size[0]), "-h", str(size[1]), workfile])
        #rc = subprocess.call(["rsvg-convert", "-w", str(size[0]), "-h", str(size[1]), "-f", "png", "-o", outfile, workfile])
        if rc != 0:
            print >>sys.stderr, "ERROR: call to inkscape failed for %s" % workfile
        pass
    pass

if options.verbose:
    print "days: %d" % (days)
    pass

for variant in variants:
    render(days, variant)
    pass

# vim: set sw=4 ts=4 et:
