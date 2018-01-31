

# run prominence network
#./scripts/submit.sh ../../../src/run_merlin.py conf/prominence_slt_arctic_demo_promark.conf

cp experiments/slt_arctic_demo_promark/prominence_model/gen/feed_forward_6_tanh/*.lab experiments/slt_arctic_demo_promark/duration_model/data/label_state_align

./scripts/submit.sh ../../../src/run_merlin.py conf/test_dur_synth_slt_arctic_demo_promark.conf

#cp experiments/slt_arctic_demo_promark/prominence_model/gen/feed_forward_6_tanh/*.lab experiments/slt_arctic_demo_promark/acoustic_model/data/label_state_align

#./scripts/submit.sh ../../../src/run_merlin.py conf/test_synth_slt_arctic_demo_promark.conf
