#!/bin/sh
BASEDIR="$HOME/countdown.o.o/svg"
LOCAL="$HOME/countdown.o.o/output/conf/2011"
REMOTE="counter.o.o:/srv/www/vhosts/0b965c33b89fac9ea53708de378f93dcda084d34/opensuse.org/counter/htdocs/conf/2011"

set -e

/bin/mkdir -p "$LOCAL"
cd "$BASEDIR"
./render-conf.py "$LOCAL" || exit 1

rsync -ap "$LOCAL/" "$REMOTE/"

