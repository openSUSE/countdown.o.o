#!/bin/bash
REMOTE_HOST="counter.o.o"
BASEDIR="/home/counter.opensuse.org/svg"
LOCAL="/home/counter.opensuse.org/output"
BINARY_LOCATION="https://raw.github.com/openSUSE/artwork/master/Marketing%20Materials/Events/openSUSE%20Conference/2013-oS-Conference/countdown-banner"
BINARY_FINAL_DATE=$(date -d "2014-11-04" +%s)
REMOTE_LOCATION="rsync://community.infra.opensuse.org/countdown"

set -e

VERBOSE=
RENDER=
REMOTE=
GIT_PULL=
while getopts 'vREBG' v; do
    case $v in
        v) VERBOSE=1;;
        R) REMOTE=1;;
        E) RENDER=1;;
        B) BINARY=1;;
        G) GIT_PULL=1;;
        *) echo "ERROR: unsupported parameter -$v">&2; exit 1;;
    esac
done
shift $(( $OPTIND - 1 ))

RFLAGS=""
[ -n "$VERBOSE" ] && RFLAGS="$RFLAGS -v"

if [ -n "$GIT_PULL" ]; then
    cd "$BASEDIR"
    GFLAGS=""
    [ -n "$VERBOSE" ] && GFLAGS="$GFLAGS --verbose"
    git pull -q --ff-only $GFLAGS
fi


mkdir -p "$LOCAL"
/bin/rm -f "$LOCAL"/*.png

if [ -n "$RENDER" ]; then
    cd "$BASEDIR"
    ./render.py $RFLAGS -k "$LOCAL"/ || exit 1
    pushd "$LOCAL" >/dev/null
    find . -maxdepth 1 -type f -name '*.png' | while read png; do
	[ -n "$VERBOSE" ] && echo "optipng $png"
        optipng "$png" &>/dev/null
    done
    popd >/dev/null
    for i in *-label.svg ; do
        cp $i "$LOCAL"/${i//-label} ;
    done
    ./mkhtml.pl "$LOCAL"/
    
    for f in *.html *.css *.js; do
        [ -e "$f" ] || continue
        cp -a "$f" "$LOCAL/"
    done
    pushd "$LOCAL/" > /dev/null
    shopt -s nullglob
    copied=
        for i in *-label*.png ; do
            j=${i//-label}
            if [ ! -e $j ] ; then
              ln -s $i ${i//-label} ;
            fi
            copied=1
        done
    shopt -u nullglob
    if [ ! -n "$copied" ]; then
       echo "There seems to be no generated images. Please check the output of \"./render.py $RFLAGS $LOCAL/\""
       exit 1
    fi
    popd > /dev/null
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
    if [ -e ~/.rsync_pass ] ; then
      source ~/.rsync_pass
    fi
    [ -n "$VERBOSE" ] && RSFLAGS="$RSFLAGS -v"
    rsync -ap --delete-after $RSFLAGS "$LOCAL/" "$REMOTE_LOCATION/"
fi
