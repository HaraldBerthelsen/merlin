
demo:
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/duration_model/data/label_state_align experiments/slt_arctic_demo/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/acoustic_model/data/label_state_align experiments/slt_arctic_demo/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/test_synthesis/prompt-lab experiments/slt_arctic_demo/test_synthesis/prompt-lab/*.lab
#	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/test_synthesis/gen-lab experiments/slt_arctic_demo/test_synthesis/gen-lab/*.lab

full:
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/duration_model/data/label_state_align experiments/slt_arctic_full/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/acoustic_model/data/label_state_align experiments/slt_arctic_full/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/test_synthesis/prompt-lab experiments/slt_arctic_full/test_synthesis/prompt-lab/*.lab
#	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/test_synthesis/gen-lab experiments/slt_arctic_full/test_synthesis/gen-lab/*.lab

demo_tobi:
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/duration_model/data/label_state_align experiments/slt_arctic_demo/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/acoustic_model/data/label_state_align experiments/slt_arctic_demo/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/test_synthesis/prompt-lab experiments/slt_arctic_demo/test_synthesis/prompt-lab/*.lab



zip:
	cd ../../..;rm pm.zip; zip -r pm.zip egs/slt_arctic/s1/*.tcl egs/slt_arctic/s1/*promark.sh egs/slt_arctic/s1/Makefile egs/slt_arctic/s1/promark egs/slt_arctic/s1/conf/*promark*.conf misc/questions/*promark*.hed
