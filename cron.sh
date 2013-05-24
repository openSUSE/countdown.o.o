#!/bin/bash
REMOTE_HOST="counter.o.o"
BASEDIR="/home/counter.opensuse.org/svg"
LOCAL="/home/counter.opensuse.org/output"
BINARY_LOCATION="https://raw.github.com/openSUSE/artwork/master/Marketing%20Materials/Events/openSUSE%20Conference/2013/countdown-banner"
BINARY_FINAL_DATE=$(date -d "2013-07-18" +%s)
REMOTE_LOCATION="counter.o.o:/srv/www/vhosts/0b965c33b89fac9ea53708de378f93dcda084d34/opensuse.org/counter/htdocs"

set -e

VERBOSE=
RENDER=
REMOTE=
while getopts 'vREB' v; do
    case $v in
        v) VERBOSE=1;;
        R) REMOTE=1;;
        E) RENDER=1;;
        B) BINARY=1;;
        *) echo "ERROR: unsupported parameter -$v">&2; exit 1;;
    esac
done
shift $(( $OPTIND - 1 ))

RFLAGS=""
[ -n "$VERBOSE" ] && RFLAGS="$RFLAGS -v"

mkdir -p "$LOCAL"
/bin/rm -f "$LOCAL"/*.png

if [ -n "$RENDER" ]; then
    cd "$BASEDIR"
    ./render.py $RFLAGS "$LOCAL"/ || exit 1
    pushd "$LOCAL" >/dev/null
    find . -maxdepth 1 -type f -name '*.png' | while read png; do
	[ -n "$VERBOSE" ] && echo "optipng $png"
        optipng "$png" &>/dev/null
    done
    popd >/dev/null

    for f in *.html *.css *.js; do
        [ -e "$f" ] || continue
        cp -a "$f" "$LOCAL/"
    done
    pushd "$LOCAL/"
        for i in *-label*.png ; do
            ln -s $i ${i//-label} ;
        done
    popd
fi

if [ -n "$BINARY" ]; then
    /bin/rm -f "$LOCAL"/*.png
    TODAY=$(date +%s)
    days_left=$(printf "%02d" $(($(($BINARY_FINAL_DATE-$TODAY+86400))/86400)))
    [ $days_left -le 00 ] && days_left=00
    for size in large medium small; do
        wget "${BINARY_LOCATION}/${days_left}-$size.png" -P "$LOCAL"
        ln -s "${days_left}-$size.png" "$LOCAL/$size.$lang.png"
        for lang in en de cs sk fr da ru pl nl fi es it el sv hr nb pt pt_BR hu ro si cn tw id bg ja wa gl ge lt tr; do
            for suffix in label nolabel; do
                ln -s "${days_left}-$size.png" "$LOCAL/$size-$suffix.$lang.png"
            done
        done
    done
fi

if [ -n "$REMOTE" ]; then
    RSFLAGS=""
    [ -n "$VERBOSE" ] && RSFLAGS="$RSFLAGS -v"
    rsync -ap --delete-after $RSFLAGS "$LOCAL/" "$REMOTE_LOCATION/"
fi
