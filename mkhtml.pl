#!/usr/bin/perl
# vim: set ts=4 sw=4 et:
use strict;
use warnings;

my %lang = (
    'en' => [ 'English' ],
    'fr' => [ 'French', 'Français' ],
    'de' => [ 'German', 'Deutsch' ],
    'nl' => [ 'Dutch', 'Nederlands' ],
    'cs' => [ 'Czech' ],
    'sk' => [ 'Slovak' ],
    'da' => [ 'Danish' ],
    'ru' => [ 'Russian' ],
    'pl' => [ 'Polish' ],
    'fi' => [ 'Finnish' ],
    'es' => [ 'Spanish', 'Español' ],
    'it' => [ 'Italian', 'Italiano' ],
    'el' => [ 'Greek' ],
    'sv' => [ 'Swedish' ],
    'hr' => [ 'Croatian', 'Hrvatska' ],
    'nb' => [ 'Norwegian' ],
    'pt' => [ 'Portuguese '],
    'pt_BR' => [ 'Brazilian Portuguese' ],
    'hu' => [ 'Hungarian' ],
    'ro' => [ 'Romanian'] ,
    'si' => [ 'Slovenian' ],
    'cn' => [ 'Chinese (traditional)' ],
    'tw' => [ 'Chinese (Taiwan)' ],
    'id' => [ 'Indonesian' ],
    'bg' => [ 'Bulgarian' ],
    'ja' => [ 'Japanese (kanji)' ],
    'wa' => [ 'Walloon', 'Wallon' ],
    'gl' => [ 'Galician', 'Galego' ],
    'ge' => [ 'Georgian' ],
);

my @order = qw(small medium large wide);

my $dir = shift;
die "must specify directory" unless defined $dir;
die "specified directory \"$dir\" does not exist or isn't a directory" unless -d $dir;

my $outfile = shift // 'index.html';

chdir($dir) or die "failed to chdir to \"$dir\": $!";

my @origs = ();
foreach my $svg (<opensuse-*.svgz>) {
    # opensuse-11.4-600x100.svgz
    my ($dist, $w, $h) = $svg =~ /^opensuse-(\d+\.\d+)-(\d+)x(\d+)\.svgz$/;
    push(@origs, {
        file => $svg,
        width => $w,
        height => $h,
    });
}

my $out;
if ($outfile eq '-') {
    $out = \*STDOUT;
} else {
    open($out, '>', $outfile) or die "failed to create \"$dir/index.html\": $!";
}
print $out <<END;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <title>openSUSE Counter Gallery</title>
        <style type="text/css">
            body {
                background: #eee;
                color: #444;
                font-family: sans;
                margin: 0 0 3em 0;
            }
            img {
                border: none;
                margin: 0;
                padding: 0;
            }
            p {
                margin: 0;
                margin-bottom: 1.5em;
            }
            h1.section {
                background: #fff;
                border: 1px solid #444;
                border-left: none;
                border-right: none;
                padding: 0.2em 0.5em 0.2em 3em;
                margin: 3em 0 0.5em 0;
            }
            p, h2, ul, dl {
                margin-left: 5%;
                margin-right: 5%;
            }
            dt {
                font-weight: bold;
                text-decoration: underline;
            }
            p.counters a {
                display: block;
                float: left;
                margin-right: 1.5em;
                margin-bottom: 3em;
            }
            h1.section, p {
                clear: both;
            }
            caption {
                padding-top: 0;
                margin-top: 0;
                text-align: top right;
            }
            #title {
                text-align: center;
                background: #fff;
                border: 1px solid #444;
                font-size: 200%;
                font-weight: bold;
                padding: 0.5em 2em;
                margin: 1em 0 2em 0;
            }
            ul {
                margin-top: 0.1em;
                padding-top: 0;
            }
            #index ul {
                padding: 0;
            }
            #index li {
                display: block;
                float: left;
                margin-right: 1em;
                width: 15m;
            }
            #snippet {
                display: block;
                background: #fff;
                border: 1px dashed #444;
                margin-top: 0.2em;
                margin-bottom: 0.2em;
                padding: 0.3em 0.5em;
                font-family: monospace;
                font-size: 120%;
            }
            h2, .svgs {
                clear: both;
            }
            h2 {
                font-size: 150%;
                font-weight: bold;
                text-decoration: underline;
                margin-top: 0;
                margin-bottom: 0;
                margin-right: 0;
            }
            .counters ul {
                padding-left: 1.5em;
            }
            .counters li {
                padding-left: 0;
                margin-left: 0;
            }
            .counters li {
                display: inline;
            }
            .counters li:before {
                content: " | ";
            }
            .counters li:first-child:before {
                content: none;
            }
        </style>
    </head>
    <body>
        <h1 id="title">openSUSE Release Counters</h1>
        <h2>How to</h2>
        <p id="howto">
            To display the openSUSE release counter on your website, blog, ..., use one of
            the following HTML snippets, depending on the size you want to use:<br/>
            <dl>
            <dt>Large (400x400):</dt>
            <dd><code id="snippet">&lt;img src="http://counter.opensuse.org/large"/&gt;</code></dd>
            <dt>Medium (256x256):</dt>
            <dd><code id="snippet">&lt;img src="http://counter.opensuse.org/medium"/&gt;</code></dd>
            <dt>Small (130x130):</dt>
            <dd><code id="snippet">&lt;img src="http://counter.opensuse.org/small"/&gt;</code></dd>
            </dl>
        </p>
        <p>
            The language in the counter image will automatically be adapted to what the person
            that <em>views</em> the page has as preferred language, falling back to English if
            we do not have a translation for that language.
        </p>
        <p>
            It is all handled on the server (counter.opensuse.org) and does not use any additional
            bandwidth on your site (except for a few bytes for the additional markup as above).
            The images are updated to reflect the number of remaining days before the release
            (at 15:00 UTF+1) on the server, and optimally cached in the browsers of the people who
            view your site.
        </p>
        <h2>Contribute</h2>
        <p>
            If you notice that your language is missing from the list, please contact
            <a href="mailto:pascal.bleser\@opensuse.org">Pascal Bleser</a> with a list of the following
            translations (not literal translations, but the best way to express the following
            English phrases in your language):
            <ul>
                <li><quote><i>n</i> days to go</quote> (before the release, might also be
                <quote>Only <i>n</i> days left</quote>), including whatever plurar and singular forms
                are specific to the grammar of your language</li>
                <li><quote>Out now!</quote>, or <quote>Available now!</quote></li>
            </ul>
        </p>
END
if (scalar(@origs) > 0) {
    print $out <<END;
        <h2>Templates</h2>
        <p>
            <ul>
END
    foreach (sort { $a->{width} - $b->{width} } @origs) {
        print $out '                <li><a href="'.$_->{file}.'">'.$_->{width}.'x'.$_->{height}.' (SVG)</a></li>', "\n";
    }
    print $out <<END;
            </ul>
        </p>
END
}

my %bylang = ();
{
    foreach my $png (<*.png>) {
        my ($size, $l, $ext) = $png =~ /^([^\.]+)\.([^\.]+)\.([^\.]+)$/;
        my $li = (exists $lang{$l}) ? $lang{$l} : undef;
        $bylang{$l} = [] unless exists $bylang{$l};
        my $a = $bylang{$l};
        my $r = { file => $png, size => $size, l => $l, li => $li };
        (my $svg = $png) =~ s/\.png$/.svgz/;
        $r->{svg} = $svg if -e $svg;
        push(@$a, $r);
    }
}

my %oi;
{
    my $i = 0;
    %oi = map { $_ => $i++ } @order;
}

print $out '    <div id="index">', "\n";
print $out '        <h2>Quick jump to language:</h2>', "\n";
print $out '        <ul>', "\n";
foreach my $l (sort keys %bylang) {
    my $pngs = $bylang{$l};
    next if scalar(@$pngs) < 1;
    my $li = $pngs->[0]->{li};
    my $h = defined($li) ? (scalar(@$li) > 1 ? $li->[1]." (".$li->[0].")" : $li->[0]) : $l;
    print $out '            <li><a href="#'.$l.'">'.$h.'</a></li>', "\n";
}
print $out '        </ul>', "\n";
print $out '    </div>', "\n";

foreach my $l (sort keys %bylang) {
    my $pngs = $bylang{$l};
    next if scalar(@$pngs) < 1;
    my $li = $pngs->[0]->{li};
    my $h = defined($li) ? (scalar(@$li) > 1 ? $li->[1]." (".$li->[0].")" : $li->[0]) : $l;
    print $out '        <h1 class="section"><a name="'.$l.'" />'.$h.'</h1>', "\n";

    print $out '        <p class="counters">',"\n";
    my @svgs = ();
    foreach my $png (sort { $oi{$a->{size}} - $oi{$b->{size}} } @$pngs) {
        print $out '            <a href="'.$png->{file}.'">', "\n";
        print $out '               <img src="'.$png->{file}.'" />', "\n";
        print $out '            </a>', "\n";
        push(@svgs, $png) if exists $png->{svg};
    }
    if (scalar(@svgs) > 1) {
        print $out '            <h2>SVGs:</h2>', "\n";
        print $out '            <ul class="svgs">', "\n";
        foreach (@svgs) {
            print $out '               <li><a href="'.$_->{svg}.'">'.$_->{size}.'</a></li>', "\n";
        }
        print $out '            </ul>', "\n";
    }
    print $out '        </p>',"\n";
}

print $out <<END;
    </body>
</html>
END

close($out) unless $outfile eq '-';


