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
    'pl' => [ 'Polish', 'Polski' ],
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
    'lt' => [ 'Lithuania' ],
    'tr' => [ 'Turkish' ],
    'zh' => [ 'Mandarin' ],
);

my %sizes = (
    'large' => [ 400, 400, 'Default' ],
    'medium' => [ 256, 256, 'Default' ],
    'small' => [ 130, 130, 'Default' ],
    'wide' => [ 600, 100, 'Default' ],
    'large-label' => [ 400, 400, 'With Labels' ],
    'medium-label' => [ 256, 256, 'With Labels' ],
    'small-label' => [ 130, 130, 'With Labels' ],
    'wide-label' => [ 600, 100, 'With Labels' ],
    'large-nolabel' => [ 400, 400, 'Without Labels' ],
    'medium-nolabel' => [ 256, 256, 'Without Labels' ],
    'small-nolabel' => [ 130, 130, 'Without Labels' ],
    'wide-nolabel' => [ 600, 100, 'Without Labels' ],
);

my @order = qw(small medium large wide);

my $dir = shift;
die "must specify directory" unless defined $dir;
die "specified directory \"$dir\" does not exist or isn't a directory" unless -d $dir;

my $outfile = shift // 'picker.html';

chdir($dir) or die "failed to chdir to \"$dir\": $!";

my @origs = ();
foreach my $svg (<opensuse-*.svg>) {
    # opensuse-11.4-600x100.svg
    my ($dist, $w, $h, $type1, $type2) = $svg =~ /^opensuse-(\d+\.\d+)-(\d+)x(\d+)-?(\w*)-?(\w*)\.svg$/;
    if ($type1 eq "") {
        $type1 = "label";
    }
    if ($type2 eq "") {
        $type2 = "default";
    }
    push(@origs, {
        file => $svg,
        width => $w,
        height => $h,
        type1 => $type1,
        type2 => $type2,
    });
}

my $out;
if ($outfile eq '-') {
    $out = \*STDOUT;
} else {
    open($out, '>', $outfile) or die "failed to create \"$dir/picker.html\": $!";
}
print $out <<END;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <title>openSUSE Counter Gallery</title>
        <style type="text/css">

          body {
            background-color:#f6f6f6;
            color:#000;
            font-family: "Open Sans", sans-serif;
            font-size: 1rem;
            font-weight: normal;
            line-height: 1.5;
            margin: 0;
          }
            
          header {
              background: #173f4f;
              padding: 0.5rem 1rem;
              position: relative;
              display: flex;
              flex-direction: row;
              flex-wrap: nowrap;
              align-items: center;
            }
            
          ul {
              flex-direction: row;
              display: flex;
              padding-left: 0;
              margin: 0;
              list-style: none;
              flex-flow: row wrap;
            }
            
          ul li {
              display: block;
              padding: 0.5em;
            }
            
          header ul li a {
              color: rgba(255, 255, 255, 0.5);
              text-decoration: none;
            }
            
          header ul li a:hover {
              color: rgba(255, 255, 255, 0.75);
              text-decoration: none;
            }
            
          .geeko {
              display: inline-block;
              padding-top: .25rem;
              padding-bottom: .25rem;
              margin-right: 1rem;
              line-height: inherit;
              white-space: nowrap;
            }
            
          header img {
              height: 2em;
              margin: 0;
              width: auto;
              display: inline-block !important;
              vertical-align: top !important;
            }

          a {
            color: #00a489;
            text-decfont-size: 2.5rem;oration: none;
          }

          a:hover {
            color: #005849;
            text-decoration: none;
          }

          h1, h2 {
            font-family: 'Open Sans Condensed';
          }

          h1 {
            font-size: 2.5rem;
          }

          h2 {
            font-size: 2rem;
          }

          .container {
            margin: 1rem auto;
            max-width: 1200px;
            padding: 0 2rem;
          }
          
          dd {
              display: block;
width: 100%;
padding: 0.5rem 0.75rem;
font-size: 1rem;
line-height: 1.25;
color: #464a4c;
background-color: #fff;
border: 1px solid #AECFCC;
border-radius: 0.25rem;
margin:0;
          }

          .responsive-image {
            width: 100%;
          }
          .responsive-text {
            position: absolute;
            background: rgba(0,0,0,0.5);
            width: calc(100% - 2em);
            bottom: 0;
            text-align: center;
          }

          .responsive-text p {
            -webkit-box-pack: justify !important;
            -ms-flex-pack: justify !important;
            justify-content: space-between !important;
            display: -webkit-box !important;
            display: -ms-flexbox !important;
            display: flex !important;
            padding: 1em;
            margin: 0;
          }

          .responsive-text span {
            color: #fff;
          }

          .cell {
            position: relative;
          }

          .cell a {
            padding: 1em 1em 0;
            display: block;
          }

          .cell img {
            display: block;
          }

          \@media screen and (min-width: 600px) {
            .grid {
              display: flex;
              flex-wrap: wrap;
              flex-direction: row;
            }
            .cell {
              width: 50%;
            }
          }

          \@media screen and (min-width: 1000px) {
            .cell {
              width: calc(100% / 3);
            }
          }

        </style>
    </head>
    <body>
        <header>
            <a class="geeko" href="https://opensuse.org">
                <img src="https://software.opensuse.org/chameleon/images/logo/logo-white.svg"/>
            </a>
            <ul>
                <li>
                    <a href="https://software.opensuse.org/search">Software</a>
                </li>
                <li>
                    <a href="https://software.opensuse.org/distributions">Download</a>
                </li>
                <li>
                    <a href="https://doc.opensuse.org">Documentation</a>
                </li>
                <li>
                    <a href="https://en.opensuse.org">Wiki</a>
                </li>
                <li>
                    <a href="https://forum.opensuse.org">Forums</a>
                </li>
            </ul>
        </header>
        <div class="container">
        <h1 id="title">openSUSE Release Counters</h1>
        <h2>How to</h2>
        <p id="howto">
            To display the openSUSE release counter on your website, blog, ..., use one of
            the following HTML snippets, depending on the size you want to use:<br/>
            <dl>
            <dt>Large (400x400):</dt>
            <dd><code id="snippet">&lt;a href="https://opensuse.org"&gt;&lt;img src="http://counter.opensuse.org/large"/&gt;&lt;/a&gt;</code></dd>
            <dt>Medium (256x256):</dt>
            <dd><code id="snippet">&lt;a href="https://opensuse.org"&gt;&lt;img src="http://counter.opensuse.org/medium"/&gt;&lt;/a&gt;</code></dd>
            <dt>Small (130x130):</dt>
            <dd><code id="snippet">&lt;a href="https://opensuse.org"&gt;&lt;img src="http://counter.opensuse.org/small"/&gt;&lt;/a&gt;</code></dd>
            <dt>Wide (600x100):</dt>
            <dd><code id="snippet">&lt;a href="https://opensuse.org"&gt;&lt;img src="http://counter.opensuse.org/wide"/&gt;&lt;/a&gt;</code></dd>
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
        </div>
END
if (scalar(@origs) > 0) {
    print $out <<END;
        <div class="container">
        <h2>Templates</h2>
        <p>
            <ul>
END
    foreach (sort { $a->{width} - $b->{width} } @origs) {
        print $out '                <li><a href="'.$_->{file}.'">'.$_->{type1}.'-'.$_->{type2}.'-'.$_->{width}.'x'.$_->{height}.' (SVG)</a></li>', "\n";
    }
    print $out <<END;
            </ul>
        </p>
        </div>
END
}

my %bylang = ();
{
    foreach my $png (<*.png>) {
        my ($sizetext, $l, $ext) = $png =~ /^([^\.]+)\.([^\.]+)\.([^\.]+)$/;
        my $li = (exists $lang{$l}) ? $lang{$l} : undef;
        my $size = (exists $sizes{$sizetext}) ? $sizes{$sizetext} : undef;
        $bylang{$l} = [] unless exists $bylang{$l};
        my $a = $bylang{$l};
        my $r = { file => $png, width => $size->[0], height => $size->[1], type => $size->[2], sizetext => $sizetext, l => $l, li => $li };
        (my $svg = $png) =~ s/\.png$/.svg/;
        $r->{svg} = $svg if -e $svg;
        push(@$a, $r);
    }
}

my %oi;
{
    my $i = 0;
    %oi = map { $_ => $i++ } @order;
}

print $out '    <div class="container">', "\n";
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
    print $out '        <h1 class="container" id="'.$l.'">'.$h.'</h1>', "\n";

    print $out '        <div class="container grid">',"\n";
    my @svgs = ();
    foreach my $png (sort { $a->{width} - $b->{width} } @$pngs) {
        print $out '            <div class="cell">', "\n";
        print $out '               <a href="'.$png->{file}.'">', "\n";
        
        
        print $out '                  <div class="responsive-text">', "\n";
        print $out '                     <p>', "\n";
        print $out '                        <span>'.$png->{width}.'x'.$png->{height}.'</span>', "\n";
        print $out '                        <span>'.$png->{type}.'</span>', "\n";
        print $out '                     </p>', "\n";
        print $out '                  </div>', "\n";
        print $out '                  <img class="responsive-image" src="'.$png->{file}.'" />', "\n";
        
        print $out '               </a>', "\n";
        print $out '            </div>', "\n";
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
    print $out '        </div>',"\n";
}

print $out <<END;
    </body>
</html>
END

close($out) unless $outfile eq '-';


