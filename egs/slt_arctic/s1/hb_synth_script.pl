#!/usr/bin/perl


    
$TEXT = <>;
if ( $TEXT eq "" ) {
    $TEXT = "This is a test";
}
chomp($TEXT);


$MERLIN = "/home/harald/git/merlin";

$festival_cmd = "/home/harald/festival/festival/bin/festival \"(set! u (Utterance Text \\\"$TEXT\\\"))\" '(utt.synth u)' '(utt.save u \"/tmp/test.utt\")' '(quit)'";

print STDERR "$festival_cmd\n";
`$festival_cmd`;


$dumpfeats_cmd = "$MERLIN/ss_dnn/scripts/dumpfeats_hb -eval $MERLIN/ss_dnn/data/resources/extra_feats.scm -relation Segment -feats $MERLIN/ss_dnn/data/resources/label.feats -output /tmp/test.feats /tmp/test.utt";
print STDERR "$dumpfeats_cmd\n";
`$dumpfeats_cmd`;

    
$make_label_cmd = "awk -f $MERLIN/ss_dnn/data/resources/HB_label-full.awk /tmp/test.feats | sed 's/pau/sil/g'> /tmp/test_full.lab";
print STDERR "$make_label_cmd\n";
`$make_label_cmd`;

$mod_label_cmd = "cat /tmp/test_full.lab | perl $MERLIN/egs/slt_arctic/s1/experiments/slt_arctic_hb/hb_make_lab.pl > /tmp/test.lab";
print STDERR "$mod_label_cmd\n";
`$mod_label_cmd`;

$cp_label_cmd = "cp /tmp/test.lab $MERLIN/egs/slt_arctic/s1/experiments/slt_arctic_hb/test_synthesis/prompt-lab/";
print STDERR "$cp_label_cmd\n";
`$cp_label_cmd`;

$echo_label_cmd = "echo test > $MERLIN/egs/slt_arctic/s1/experiments/slt_arctic_hb/test_synthesis/test_id_list.scp";
print STDERR "$echo_label_cmd\n";
`$echo_label_cmd`;

#$synthesis_cmd = "cd $MERLIN/egs/slt_arctic/s1; ./run_hb.sh 2> /dev/null";
#print "$synthesis_cmd\n";
#`$synthesis_cmd`;

# $play_cmd = "play $MERLIN/egs/slt_arctic/s1/experiments/slt_arctic_hb/test_synthesis/wav/test.wav";
# print "$play_cmd\n";
# `$play_cmd`;

# $wsurf_cmd = "wavesurfer $MERLIN/egs/slt_arctic/s1/experiments/slt_arctic_hb/test_synthesis/wav/test.wav";
# print "$wsurf_cmd\n";
# `$wsurf_cmd`;
