$labdir = $ARGV[0];


@labfiles = glob("$labdir/*.lab");

$tmpfile = "/tmp/tmplabfile";

foreach $labfile (@labfiles) {
    chomp($labfile);
    print "$labfile\n";

    open(LAB, $labfile);
    open(OUT, ">$tmpfile");

    while (<LAB>) {
	chomp;
	$line = $_;

	$orgline = $line;
	
	$line =~ s/ao\+/aao/g;
	$line =~ s/ae\+/aae/g;
	$line =~ s/oe\+/ooe/g;

	$line =~ s/a\+/aa/g;
	$line =~ s/e\+/ee/g;
	$line =~ s/i\+/ii/g;
	$line =~ s/o\+/oo/g;
	$line =~ s/u\+/uu/g;
	$line =~ s/y\+/yy/g;

	$line =~ s/@([-@=^+])/eh\1/g;

#	if ( $line ne $orgline ) {
#	    print "$line\n$orgline\n";
#	    exit;
#	}
	print OUT "$line\n";	
	
    }
    close(OUT);
    close(LAB);

    `mv $tmpfile $labfile`;
	

}
