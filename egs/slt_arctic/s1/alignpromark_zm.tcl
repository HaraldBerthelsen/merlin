



proc readpromarkdata {fn} {
    set f [open $fn]
    set prodata [split [string trim [read $f]] \n]
    close $f
 
    
    set currfile ""

    foreach elem [lrange $prodata 1 end] {
	
	set line [split $elem \t]
	set word [lindex $line $::wordindex]
	set file [lindex $line $::fileindex]
	if {$file!=$currfile} {
	    set currfile $file
	    set wordnr 0
	}
	if {$word != "."} {
	    incr wordnr
	} else {
	    continue
	}
#	set interval [lindex $line 5]
	set prominence [string trim [lindex $line $::promindex] \[\]]
	set maxprom 0 
	foreach val [split $prominence ,] {
	    if {$val>$maxprom} {
		set maxprom $val
	    }
	}
	set ::prom($file,$wordnr) $maxprom
	if {[string match "*'s" $word]} {
	    incr wordnr
	    set ::prom($file,$wordnr) $maxprom
	}
    }
}

#HB to be able to read the two formats
set csvformat [lindex $argv 0]

if {$csvformat == "demo"} {
    #For the A/B_promark_raters files
    set wordindex 1
    set fileindex 4
    set promindex 8
    readpromarkdata promark/A_promark_raters.csv
    readpromarkdata promark/B_promark_raters.csv
} elseif {$csvformat == "full"} {
    #For the tagger_slt.csv file
    set wordindex 2
    set fileindex 4
    set promindex 6
    readpromarkdata promark/tagger_slt.csv
} elseif {$csvformat == "tobi"} {
    #For the tagger_slt.csv file
    set wordindex 2
    set fileindex 4
    #tobi features
    set promindex 8
    readpromarkdata promark/tagger_slt.csv
} else {
    puts "csvformat: $csvformat not supported"
    exit
}

set outdir [lindex $argv 1]
# experiments/slt_arctic_demo_promark/duration_model/data/label_phone_align/

puts outdir=$outdir

#exec mkdir -p $outdir

# parray prom

foreach file [lrange $argv 2 end] {
    set f [open $file]
    set data [split [string trim [read $f]] \n]
    close $f
 
 
    set filename [file tail [file root $file]]_slt
    set outfile $outdir/[file tail $file]

    puts $filename...

    set outdata {}
    set accumword 0
    set currphrase 1
    foreach line $data {
	
	if {![regexp {@x\+} $line]} {
	    if [regexp {@(\d+)\=} $line all phraseinutt] {
		# puts "phraseinutt=$phraseinutt"
	    }
	    if {$phraseinutt != $currphrase} {
		incr accumword $wordinphrase
		set currphrase $phraseinutt
	    }
	    if [regexp {@(\d+)\+} $line all wordinphrase] {
		# puts "wordinphrase=$wordinphrase"
		
		set wordnumber [expr $wordinphrase+$accumword]
		# puts "wordnumber: $wordnumber"
		# puts "prom($filename,$wordnumber): $prom($filename,$wordnumber)"
	    }
	    if {[catch {set prominence $prom($filename,$wordnumber)} err]} {
		puts "WARNING: $err"

		#HB What to do if the file is not in the csv list? Now setting prominence to 0,
		#just to be able to continue
		set prominence 0
		#exit 1
	    }
	} else {
	    set prominence 0
	}
	if [regexp {(.+)(\[\d+\])$} $line match first last] {
	    if {$csvformat == "tobi"} {
		lappend outdata $first/K:[string trim $prominence]$last
	    } else {
		lappend outdata $first/K:[expr int(100*[string trim $prominence])]$last
	    }
	} else {
	    if {$csvformat == "tobi"} {
		lappend outdata $line/K:[string trim $prominence]
	    } else {
		lappend outdata $line/K:[expr int(100*[string trim $prominence])]
	    }
	}
    }

    #HB This is a sanity check to see that the number of words in lab and csv are the same.
    #Good, but now I want to continue with a warning if the filename is not in the csv file at all
    #Adding a test for that
    if {[info exists prom($filename,*)]} {
	if {$wordnumber != [llength [array names prom $filename,*]]} {
	    error "something went wrong"
	}
    }

 #   parray prom $filename,*

    set f [open $outfile w]
    puts $f [join $outdata \n]
    close $f
}
