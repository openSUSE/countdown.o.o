#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 et:
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
import re
import subprocess
import tempfile
import shutil
import atexit

# 11.0:
# VERSION = "11.0"
# RELEASE = datetime.datetime(2008, 6, 19, 15, 0, 0)

# 11.1:
# VERSION = "11.1"
# RELEASE = datetime.datetime(2008, 12, 18, 15, 0, 0)

# 11.2:
# VERSION = "11.2"
# RELEASE = datetime.datetime(2009, 11, 12, 15, 0, 0)

# 11.3:
#VERSION = "11.3"
#RELEASE = datetime.datetime(2010, 7, 15, 14, 0, 0)

# 11.4:
VERSION = "11.4"
RELEASE = datetime.datetime(2011, 3, 10, 14, 0, 0)

###--- no need to change below this line ---###

PREFIX = "opensuse-%s" % VERSION
# dimensions are tuples of (width,height,name)
sizes = [(600,100,"wide"), (400,400,"large"), (256,256,"medium"), (130,130,"small")]

options = None
optionParser = OptionParser(usage="%prog [options] [<output directory>]",
        description="render countdown image")
optionParser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='be verbose')
optionParser.add_option('-l', '--lang', action='append', dest='lang', default=[], help='language to render')
optionParser.add_option('-k', '--keep', action='store_true', dest='keep', default=False, help='keep SVG files')
optionParser.add_option('-s', '--size', action='append', dest='sizes', default=[], help='sizes to render')
(options, args) = optionParser.parse_args(sys.argv)

if len(options.sizes) == 0:
    options.sizes = [x[2] for x in sizes]
    pass

def msg_ru(n):
    if (n != 11) and (n % 10 == 1):
        pre = u'Остался'
    else:
        pre = u'Осталось'
    if n % 10 == 1 and n % 100 != 11:
        return pre, u'день'
    if n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return pre, u'дня'
    return pre, u'дней'

def msg_sk(n):
    if n == 1:
        post = u'deň'
    elif n <= 4:
        post = u'dni'
    else:
        post = u'dní'
    return u'Už len', post

def msg_lt(n):
    if (n % 10 == 1) and (n != 11):
        post = 'dienų'
    else:
        post = 'dienos'
    return u'Pasirodys po', post

avail = {
        'en': u'Out\nnow!',
        'de': u'Jetzt\nverfügbar!',
        'cs': u'Nyní\ndostupné!',
        'sk': u'Stahuj\nteraz!',
        'fr': u'Disponible\nmaintenant!',
        'da': u'Ude\nnu!',
        'ru': u'Уже\nвышла',
        'pl': u'Ju\u017C\ndost\u0119pny!',
        'nl': u'Nu\nbeschikbaar!',
        'fi': u'Nyt\nsaatavissa!',
        'es': u'Ya\ndisponible!',
        'it': u'Disponibile\nora!',
        'el': u'Διαθέσιμο\nτώρα!',
        'sv': u'Ute\nnu!',
        'hr': u'Sad\ndostupan!',
        'nb': u'Ute\nnå!',
        'pt': u'Já\ndisponível!',
        'pt_BR': u'Baixe\nagora!',
        'hu': u'Megjelent',
        'ro': u'Disponibil\nacum!',
        'si': u'Zunaj\nZdaj!',
        'cn': u'立即下载',
        'tw': u'立即下載',
        'id': u'Download\nsekarang',
        'bg': u'довнлоад\nсега!',
        'ja': u'好評\n提供中！',
        'wa': u'Disponibe\ndo côp!',
        'gl': u'Xa está\ndispoñible!',
        'ge': u'არსებული',
        'lt': u'Išleista!',
        }

almost = {
        'en': [u'Release in', [u'hours!', u'hour!']],
        'fr': [u'Plus que', [u'heures!', u'heure!']],
        'de': [u'Verfügbar in', [u'Stunden!', u'Stunde!']],
        'it': [u'Disponibile in', [u'ore!', u'ora!']],
        'da': [u'Udgives om', [u'timer!', u'time!']],
        'es': [u'Disponible en', [u'horas!', u'hora!']],
        'lt': [u'Pasirodys po', [u'val.', u'val.']],
}

m = {
        'en': ['Only', 'days to go', '', 'day to go'],
        'de': ['Nur noch', 'Tage', 'Nur noch', 'Tag'],
        'cs': ['', u'dní do vydání'],
        'sk': msg_sk,
        'fr': ['Plus que', 'jours', "Plus qu'", 'jour'],
        'da': ['', 'dage tilbage'],
        'ru': msg_ru,
        'pl': [u'Zostało', 'dni'],
        'nl': ['Nog', 'dagen', 'Nog', 'dag'],
        'fi': ['', u'päivää\njäljellä'],
        'es': ['Quedan', u'días', 'Quedan', u'dìa'],
        'it': ['', 'giorni al via', '', 'giorno al via'],
        #'el': ['', u'περισσότερες\nμέρες', u'Τελευταία|Μέρα'],
        'el': [u'Μόνο', u'μέρες ακόμη'],
        'sv': ['', 'dagar kvar'],
        'hr': [u'Još', 'dana'],
        'nb': ['', 'dager igjen'],
        'pt': ['Faltam', 'dias', 'Falta', 'dia'],
        'pt_BR': ['Faltam', 'dias', 'Falta', 'dia'],
        'hu': [u'Még', 'nap'],
        'ro': [u'Încă', 'zile'],
        'id': ['', u'hari lagi'],
        'bg': [u'още', u'дин', u'още', u'ден'],
        'ja': [u'いよいよ登場！\nあと', u'日'],
        'wa': [u'Co', u'djoûs a\nratinde', u'Co', u'djoû a ratinde'],
        'tw': [u'倒數', u'天'],
        'gl': [u'Dispoñible en', u'días', u'Dispoñible en', u'día'],
        'lt': msg_lt,
        }

font_override = {
        'cn': 'Droid Sans Fallback',
        'tw': 'Droid Sans Fallback',
        #'ja': 'Droid Sans Fallback',
        'ja': 'IPAGothic',
        #'cn': "AR PL SungtiL GB",
        #'tw': "AR PL KaitiM Big5",
        }

font_to_replace = u'DejaVu Sans'
default_font = 'FifthLeg'

if len(args) >= 2:
    prefix = args[1]
else:
    prefix = "../output/%s" % VERSION
    pass

if len(options.lang) > 0:
    languages = options.lang
else:
    languages = list(set(m.keys() + avail.keys()))
    pass

diff = (RELEASE - datetime.datetime.now())
days = diff.days
color = (255, 255, 255, 255)

workdir = None

def on_exit():
    if workdir != None and os.path.exists(workdir):
        shutil.rmtree(workdir)
        pass
    pass
atexit.register(on_exit)

workdir = tempfile.mkdtemp(prefix='countdown', suffix='tmp')
dev_null = open('/dev/null', 'w')

def sjoin(a, sep, b):
    r = a
    if len(a) > 0 and len(b) > 0:
        r += sep
        pass
    r += b
    return r

def render(lang, truelang, top1, top2, center, bottom1, bottom2, template_variant=None):
    x = unicode(center).encode('ascii', 'xmlcharrefreplace')
    y = unicode(top1).encode('ascii', 'xmlcharrefreplace')
    yy = unicode(top2).encode('ascii', 'xmlcharrefreplace')
    z = unicode(bottom1).encode('ascii', 'xmlcharrefreplace')
    zz = unicode(bottom2).encode('ascii', 'xmlcharrefreplace')
    ly = reduce(lambda x,y: sjoin(x, u" ", y), [y, yy])
    lz = reduce(lambda x,y: sjoin(x, u" ", y), [z, zz])

    font_repl = None
    if truelang in font_override:
        font_repl = font_override[truelang]
    else:
        font_repl = default_font
        pass

    for size in sizes:
        if not (size[2] in options.sizes):
            continue

        if template_variant == None:
            template = "%s-%dx%d.svg" % (PREFIX, size[0], size[1])
        else:
            template = "%s-%dx%d-%s.svg" % (PREFIX, size[0], size[1], template_variant)
            pass

        outfile = "%s/%s.%s.png" % (prefix, size[2], lang)

        if options.verbose:
            print "%s / %s: %s -> %s" % (lang, size[2], template, outfile)
            pass

        workfile = os.path.join(workdir, "work.svg")
        out = open(workfile, "wb")
        for line in fileinput.FileInput(template, mode="rb"):
            line = unicode(line)
            line = line.replace(u"@@", x).replace(u"@TOPC@", y).replace(u"@TOP@", yy).replace(u"@BOTTOM@", z).replace(u"@BOTTOMC@", zz)
            line = line.replace(u"@_TOP_@", ly).replace(u"@_BOTTOM_@", lz)
            if font_repl != None:
                line = line.replace(font_to_replace, unicode(font_repl))
                pass
            out.write(line)
            pass
        out.close()

        #rc = subprocess.call(["rsvg-convert", "-w", str(size[0]), "-h", str(size[1]), "-f", "png", "-o", outfile, workfile])

        rc = subprocess.call(["inkscape", "-z", "--export-png=%s" % outfile, "--export-area-page", "-w", str(size[0]), "-h", str(size[1]), workfile], stdout=dev_null)
        if options.keep:
            svg_outfile = "%s/%s.%s.svg" % (prefix, size[2], lang)
            shutil.copyfile(workfile, svg_outfile)
            print "SVG saved as %s" % svg_outfile
            pass

        if rc != 0:
            print >>sys.stderr, "ERROR: call to inkscape failed for %s" % workfile
        pass
    pass

def render_outnow(lang, top, bottom):
    y = unicode(top).encode('ascii', 'xmlcharrefreplace')
    z = unicode(bottom).encode('ascii', 'xmlcharrefreplace')

    if options.verbose:
        sys.stdout.write("%s:" % lang)
        sys.stdout.flush()
        pass

    for size in sizes:
        template = "%s-%dx%d-outnow.svg" % (PREFIX, size[0], size[1])

        workfile = os.path.join(workdir, "work.svg")
        out = open(workfile, "wb")
        for line in fileinput.FileInput(template, mode="rb"):
            line = unicode(line).replace(u"@TOP@", y).replace(u"@BOTTOM@", z)
            out.write(line)
            pass
        out.close()

        if options.verbose:
            sys.stdout.write(" %s" % size[2])
            sys.stdout.flush()
            pass

        outfile = "%s/%s.%s.png" % (prefix, size[2], lang)
        rc = subprocess.call(["inkscape", "-z", "--export-png=%s" % outfile, "--export-area-page", "-w", str(size[0]), "-h", str(size[1]), workfile], stdout=dev_null)
        if options.keep:
            svg_outfile = "%s/%s.%s.svg" % (prefix, size[2], lang)
            shutil.copyfile(workfile, svg_outfile)
            print "SVG saved as %s" % svg_outfile
            pass

        if rc != 0:
            print >>sys.stderr, "ERROR: call to inkscape failed for %s" % workfile
        pass

    if options.verbose:
        print
        pass
    pass


if options.verbose:
    print "days: %d" % (days)
    pass

if days == 0 and diff.seconds > 0:
    for lang in languages:
        hours = ((diff.seconds / 3600) + 1)
        text = "%02d" % (hours)
        post2 = ""

        if lang in almost:
            m = almost[lang]
            truelang = lang
        else:
            m = almost['en']
            truelang = 'en'
            pass
        top = m[0]
        if hours > 1:
            post = m[1][0]
        else:
            post = m[1][1]
            pass

        render(lang, truelang, "", top, text, post, post2, "almost")
        pass
    pass

elif days <= 0:
    for lang in languages:
        if avail.has_key(lang):
            text = avail[lang]
        else:
            text = avail['en']
            pass
        parts = text.split("\n")
        if len(parts) == 1:
            render_outnow(lang, parts[0], "")
        else:
            render_outnow(lang, parts[0], parts[1])
            pass
        pass
    pass
else:
    for lang, msg in m.items():
        if not lang in languages:
            continue
        whole = None
        text = str(days)
        post2 = ''
        pre0 = ''
        if callable(msg):
            pre, post = msg.__call__(days)
        elif len(msg) == 4:
            if days > 1:
                pre = msg[0]
                post = msg[1]
            else:
                pre = msg[2]
                post = msg[3]
                pass
            pass
        elif len(msg) == 2:
            pre = msg[0]
            post = msg[1]
        elif len(msg) == 3:
            if days > 1:
                pre = msg[0]
                post = msg[1]
            else:
                pre = None
                post = None
                text = None
                whole = msg[2]
                pass
            pass
        else:
            print >>sys.stderr, "unsupported msg: %s" % msg
            sys.exit(1)
            pass

        if post != None and "\n" in post:
            parts = post.split("\n")
            post = parts[0]
            post2 = parts[1]
            pass

        if pre != None and "\n" in pre:
            parts = pre.split("\n")
            pre0 = parts[0]
            pre = parts[1]
            pass

        render(lang, lang, pre0, pre, text, post, post2)
        pass
    pass

if os.path.exists("/tmp/work.svg"):
    os.remove("/tmp/work.svg")
    pass

