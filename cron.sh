#!/bin/bash
REMOTE_HOST="counter.o.o"
BASEDIR="/home/counter.opensuse.org/svg"
LOCAL="/home/counter.opensuse.org/output"
REMOTE="counter.o.o:/srv/www/vhosts/0b965c33b89fac9ea53708de378f93dcda084d34/opensuse.org/counter/htdocs"

set -e

VERBOSE=''
RENDER=1
while getopts 'vRE' v; do
    case $v in
        v) VERBOSE=1;;
        R) REMOTE='';;
        E) RENDER='';;
        *) echo "ERROR: unsupported parameter -$v">&2; exit 1;;
    esac
done
shift $(( $OPTIND - 1 ))

RFLAGS=""
[ -n "$VERBOSE" ] && RFLAGS="$RFLAGS -v"

cd "$BASEDIR"
mkdir -p "$LOCAL"
if [ -n "$RENDER" ]; then
    /bin/rm -f "$LOCAL"/*.png
    ./render.py $RFLAGS "$LOCAL"/ || exit 1
    pushd "$LOCAL" >/dev/null
    find . -type f -maxdepth 1 -name '*.png' | while read png; do
	[ -n "$VERBOSE" ] && echo "optipng $png"
        optipng "$png" &>/dev/null
    done
    popd >/dev/null

    # workaround, remove once darix has updated the rewrite config:
    mkdir -p "$LOCAL/12.1"
    /bin/rm -f "$LOCAL/12.1"/*.png
    /bin/cp -a *.png "$LOCAL/12.1/"
fi

if [ -n "$REMOTE" ]; then
    RSFLAGS=""
    [ -n "$VERBOSE" ] && RSFLAGS="$RSFLAGS -v"
    rsync -ap --delete-after $RSFLAGS "$LOCAL/" "$REMOTE/"
fi

