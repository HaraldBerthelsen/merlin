while (<>) {
    chomp;
    $line = $_;
    for ($i=2; $i<7; $i++) {
	print "${line}[$i]\n";
    }
}
