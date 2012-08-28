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

VERSION = "12.2"
RELEASE = datetime.datetime(2012, 9, 5, 14, 0, 0)

VARIANTS = ["label", "nolabel"]

###--- no need to change below this line ---###

PREFIX = "opensuse-%s" % VERSION
# dimensions are tuples of (width,height,name)
sizes = [(600,100,"wide"), (400,400,"large"), (256,256,"medium"), (130,130,"small")]
varlist = [""] + ["-%s" % (x) for x in VARIANTS]

options = None
optionParser = OptionParser(usage="%prog [options] [<output directory>]",
        description="render countdown image")
optionParser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='be verbose')
optionParser.add_option('-l', '--lang', action='append', dest='lang', default=[], help='language to render')
optionParser.add_option('-k', '--keep', action='store_true', dest='keep', default=False, help='keep SVG files')
optionParser.add_option('-s', '--size', action='append', dest='sizes', default=[], help='sizes to render')
optionParser.add_option('-d', '--days', dest='forced_days', type='int', default=None, help='force the amount of remaining days', metavar='DAYS')
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
        post = u'dienų'
    else:
        post = u'dienos'
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
        'cn': u'盛装发布！',
        'tw': u'盛裝發佈！',
        'id': u'Download\nsekarang',
        'bg': u'довнлоад\nсега!',
        'ja': u'好評\n提供中！',
        'wa': u'Disponibe\ndo côp!',
        'gl': u'Xa está\ndispoñible!',
        'ge': u'არსებული',
        'lt': u'Išleista!',
        'tk': u'Çıktı',
        }

almost = {
        'en': [u'Release in', [u'hours!', u'hour!']],
	'cn': [u'即刻登场', [u'小时！', u'小时！']],
        'tw': [u'即刻登場', [u'小時！', u'小時！']],
        'fr': [u'Plus que', [u'heures!', u'heure!']],
        'de': [u'Verfügbar in', [u'Stunden!', u'Stunde!']],
        'it': [u'Disponibile in', [u'ore!', u'ora!']],
        'da': [u'Udgives om', [u'timer!', u'time!']],
        'es': [u'Disponible en', [u'horas!', u'hora!']],
        'lt': [u'Pasirodys po', [u'val.', u'val.']],
        'tk': [u'', [u'saat sonra karşınızda!', u'saat sonra karşınızda!']],
}

m = {
        'en': [u'Only', u'days to go', u'', u'day to go'],
        'de': [u'Nur noch', u'Tage', u'Nur noch', u'Tag'],
        'cs': [u'', u'dní do vydání'],
        'sk': msg_sk,
        'fr': [u'Plus que', u'jours', u"Plus qu'", u'jour'],
        'da': [u'', u'dage tilbage'],
        'ru': msg_ru,
        'pl': [u'Zostało', u'dni'],
        'nl': [u'Nog', u'dagen', u'Nog', u'dag'],
        'fi': [u'', u'päivää\njäljellä'],
        'es': [u'Quedan', u'días', u'Quedan', u'dìa'],
        'it': [u'', u'giorni al via', u'', u'giorno al via'],
        #'el': ['', u'περισσότερες\nμέρες', u'Τελευταία|Μέρα'],
        'el': [u'Μόνο', u'μέρες ακόμη'],
        'sv': [u'', u'dagar kvar'],
        'hr': [u'Još', u'dana'],
        'nb': [u'', u'dager igjen'],
        'pt': [u'Faltam', u'dias', u'Falta', u'dia'],
        'pt_BR': [u'Faltam', u'dias', u'Falta', u'dia'],
        'hu': [u'Még', u'nap'],
        'ro': [u'Încă', u'zile'],
        'id': [u'', u'hari lagi'],
        'bg': [u'още', u'дин', u'още', u'ден'],
        'ja': [u'いよいよ登場！\nあと', u'日'],
        'wa': [u'Co', u'djoûs a\nratinde', u'Co', u'djoû a ratinde'],
	'cn': [u'倒数', u'天'],
        'tw': [u'倒數', u'天'],
        'gl': [u'Dispoñible en', u'días', u'Dispoñible en', u'día'],
        'lt': msg_lt,
        'tr': [u'', u'gün kaldı'],
}

extra = {
        'tr': {
            u'Linux for open minds': u'Açık fikirliler için linux',
        }
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
    outdir = args[1]
else:
    outdir = "../output/%s" % VERSION
    pass

if len(options.lang) > 0:
    languages = options.lang
else:
    languages = list(set(m.keys() + avail.keys()))
    pass

if options.forced_days != None:
    days = options.forced_days
    seconds = 0
else:
    diff = (RELEASE - datetime.datetime.now())
    days = diff.days
    seconds = diff.seconds
    pass

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

def call_render(workfile, outfile, width, height):
    # can't use rsvg as the black outline around placeholers is
    # stored in a way only inkscape can process
    #rc = subprocess.call(["rsvg-convert", "-w", str(width), "-h", str(height), "-f", "png", "-o", outfile, workfile])
    rc = subprocess.call(["inkscape", "-z", "--export-png=%s" % outfile, "--export-area-page", "-w", str(width), "-h", str(height), workfile], stdout=dev_null)
    return rc


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

        if y != None and len(y) > 0:
            t = "-top"
        else:
            t = None
            pass

        for var in varlist:
            if template_variant == None:
                if t != None:
                    template = "%s-%dx%d%s%s.svg" % (PREFIX, size[0], size[1], var, t)
                if t == None or not os.path.exists(template):
                    template = "%s-%dx%d%s.svg" % (PREFIX, size[0], size[1], var)
            else:
                if t != None:
                    template = "%s-%dx%d%s%s-%s.svg" % (PREFIX, size[0], size[1], var, t, template_variant)
                if t == None or not os.path.exists(template):
                    template = "%s-%dx%d%s-%s.svg" % (PREFIX, size[0], size[1], var, template_variant)
                pass

            if not os.path.exists(template):
                if options.verbose:
                    print "skipping %s / %s / %s: template \"%s\" does not exist" % (lang, var, size[2], template)
                    pass
                continue

            outfile = "%s/%s%s.%s.png" % (outdir, size[2], var, lang)

            if options.verbose:
                print "%s / %s / %s: %s -> %s" % (lang, var, size[2], template, outfile)
                pass

            workfile = os.path.join(workdir, "work.svg")
            out = open(workfile, "wb")
            for line in fileinput.FileInput(template, mode="rb"):
                line = unicode(line)
                line = line.replace(u"@@", x).replace(u"@TOPC@", y).replace(u"@TOP@", yy).replace(u"@BOTTOM@", z).replace(u"@BOTTOMC@", zz)
                line = line.replace(u"@_TOP_@", ly).replace(u"@_BOTTOM_@", lz)
                line = line.replace(u"##.#", VERSION)

                if lang in extra:
                    for s, r in extra[lang].iteritems():
                        line = line.replace(s, unicode(r).encode('ascii', 'xmlcharrefreplace'))
                        pass
                    pass

                if font_repl != None:
                    line = line.replace(font_to_replace, unicode(font_repl))
                    pass
                out.write(line)
                pass
            out.close()

	    rc = call_render(workfile, outfile, size[0], size[1])
            if options.keep:
                svg_outfile = "%s/%s%s.%s.%s.svg" % (outdir, PREFIX, var, size[2], lang)
                shutil.copyfile(workfile, svg_outfile)
                if options.verbose:
                    print "SVG saved as %s" % svg_outfile
                    pass
                pass

            if rc != 0:
                print >>sys.stderr, "ERROR: call to inkscape failed for %s" % workfile
            pass
        pass
    pass

def render_outnow(lang, truelang, top, bottom, template_variant=None):
    y = unicode(top).encode('ascii', 'xmlcharrefreplace')
    z = unicode(bottom).encode('ascii', 'xmlcharrefreplace')

    if options.verbose:
        sys.stdout.write("%s:" % lang)
        sys.stdout.flush()
        pass
    
    font_repl = None
    if truelang in font_override:
        font_repl = font_override[truelang]
    else:
        font_repl = default_font
        pass

    for size in sizes:
        if not (size[2] in options.sizes):
            continue

        if y != None and len(y) > 0:
            t = "-top"
        else:
            t = None
            pass

        for var in varlist:
            if template_variant == None:
                if t != None:
                    template = "%s-%dx%d-outnow%s%s.svg" % (PREFIX, size[0], size[1], var, t)
                if t == None or not os.path.exists(template):
                    template = "%s-%dx%d-outnow%s.svg" % (PREFIX, size[0], size[1], var)
            else:
                if t != None:
                    template = "%s-%dx%d-outnow%s%s-%s.svg" % (PREFIX, size[0], size[1], var, t, template_variant)
                if t == None or not os.path.exists(template):
                    template = "%s-%dx%d-outnow%s-%s.svg" % (PREFIX, size[0], size[1], var, template_variant)
                pass

            if not os.path.exists(template):
                if options.verbose:
                    print "skipping %s / %s / %s: template \"%s\" does not exist" % (lang, var, size[2], template)
                    pass
                continue

            outfile = "%s/%s%s.%s.png" % (outdir, size[2], var, lang)

            if options.verbose:
                print "%s / %s / %s: %s -> %s" % (lang, var, size[2], template, outfile)
                pass

            workfile = os.path.join(workdir, "work.svg")
            out = open(workfile, "wb")
            for line in fileinput.FileInput(template, mode="rb"):
                line = unicode(line).replace(u"@TOP@", y).replace(u"@BOTTOM@", z)
                line = line.replace(u"##.#", VERSION)
                if lang in extra:
                    for s, r in extra[lang].iteritems():
                        line = line.replace(s, unicode(r).encode('ascii', 'xmlcharrefreplace'))
                        pass
                    pass
                if font_repl != None:
                    line = line.replace(font_to_replace, unicode(font_repl))
                    pass
                out.write(line)
                pass
            out.close()

	    rc = call_render(workfile, outfile, size[0], size[1])
            if options.keep:
                svg_outfile = "%s/%s%s.%s.%s.svg" % (outdir, PREFIX, var, size[2], lang)
                shutil.copyfile(workfile, svg_outfile)
                if options.verbose:
                    print "SVG saved as %s" % svg_outfile
                    pass
                pass

            if rc != 0:
                print >>sys.stderr, "ERROR: call to inkscape failed for %s" % workfile
            pass
        pass
    pass

if options.verbose:
    print "days: %d" % (days)
    pass

if not os.path.exists(outdir):
    os.makedirs(outdir)
    pass

if days == 0 and seconds > 0:
    for lang in languages:
        hours = ((seconds / 3600) + 1)
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
        if not lang in languages:
            continue

        if avail.has_key(lang):
            text = avail[lang]
        else:
            text = avail['en']
            pass

        if lang in almost:
            m = almost[lang]
            truelang = lang
        else:
            m = almost['en']
            truelang = 'en'
            pass

        parts = text.split("\n")
        if len(parts) == 1:
            render_outnow(lang, truelang, parts[0], "")
        else:
            render_outnow(lang, truelang, parts[0], parts[1])
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

        if lang in almost:
            m = almost[lang]
            truelang = lang
        else:
            m = almost['en']
            truelang = 'en'
            pass

        render(lang, truelang, pre0, pre, text, post, post2)
        pass
    pass

