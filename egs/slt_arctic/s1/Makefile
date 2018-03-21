

#demo:
#	tclsh alignpromark.tcl demo-prom experiments/slt_arctic_demo_promark/prominence_model/data/label_state_align experiments/slt_arctic_demo/duration_model/data/label_state_align/*.lab

demo:
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/prominence_model/data/label_state_align experiments/slt_arctic_demo_promark/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/acoustic_model/data/label_state_align experiments/slt_arctic_demo_promark/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/test_synthesis/prompt-lab experiments/slt_arctic_demo_promark/test_synthesis/prompt-lab/*.lab

demo-phone_align:
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/prominence_model/data/label_phone_align experiments/slt_arctic_demo_promark/duration_model/data/label_phone_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/acoustic_model/data/label_phone_align experiments/slt_arctic_demo_promark/acoustic_model/data/label_phone_align/*.lab
	tclsh alignpromark.tcl demo experiments/slt_arctic_demo_promark/test_synthesis/prompt-lab experiments/slt_arctic_demo_promark/test_synthesis/prompt-lab/*.lab


full:
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/duration_model/data/label_state_align experiments/slt_arctic_full/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/acoustic_model/data/label_state_align experiments/slt_arctic_full/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/test_synthesis/prompt-lab experiments/slt_arctic_full/test_synthesis/prompt-lab/*.lab

full-syl:
#	cp -pr experiments/slt_arctic_full experiments/slt_arctic_full_promark
#	cd experiments; ln -sf slt_arctic_full_promark  slt_arctic_full_promark_syl
	tclsh alignpromark.tcl sylprom experiments/slt_arctic_full_promark/duration_model/data/label_state_align experiments/slt_arctic_full/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl sylprom experiments/slt_arctic_full_promark/acoustic_model/data/label_state_align experiments/slt_arctic_full/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl sylprom experiments/slt_arctic_full_promark/test_synthesis/prompt-lab experiments/slt_arctic_full/test_synthesis/prompt-lab/*.lab

#	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/test_synthesis/gen-lab experiments/slt_arctic_full/test_synthesis/gen-lab/*.lab

demo_tobi:
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/duration_model/data/label_state_align experiments/slt_arctic_demo/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/acoustic_model/data/label_state_align experiments/slt_arctic_demo/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_demo_tobi/test_synthesis/prompt-lab experiments/slt_arctic_demo/test_synthesis/prompt-lab/*.lab

syltest: 
	tclsh alignpromark.tcl sylprom experiments/slt_arctic_demo_promark/duration_model/data/label_state_align experiments/slt_arctic_demo/duration_model/data/label_state_align/arctic_a0001.lab

full_tobi:
	tclsh alignpromark.tcl tobi experiments/slt_arctic_full_tobi/duration_model/data/label_state_align experiments/slt_arctic_full/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_full_tobi/acoustic_model/data/label_state_align experiments/slt_arctic_full/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl tobi experiments/slt_arctic_full_tobi/test_synthesis/prompt-lab experiments/slt_arctic_full/test_synthesis/prompt-lab/*.lab
#	tclsh alignpromark.tcl full experiments/slt_arctic_full_promark/test_synthesis/gen-lab experiments/slt_arctic_full/test_synthesis/gen-lab/*.lab


zip:
	cd ../../..;rm pm.zip; zip -r pm.zip egs/slt_arctic/s1/*.tcl egs/slt_arctic/s1/*promark.sh egs/slt_arctic/s1/Makefile egs/slt_arctic/s1/promark egs/slt_arctic/s1/conf/*promark*.conf misc/questions/*promark*.hed

adbks:
	tclsh alignpromark.tcl adbks experiments/audiobooks_promark/prominence_model/data/label_state_align experiments/audiobooks_promark/duration_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl adbks experiments/audiobooks_promark/acoustic_model/data/label_state_align experiments/audiobooks_promark/acoustic_model/data/label_state_align/*.lab
	tclsh alignpromark.tcl adbks experiments/audiobooks_promark/test_synthesis/prompt-lab experiments/audiobooks_promark/test_synthesis/prompt-lab/*.lab
#	tclsh alignpromark.tcl adbks experiments/audiobooks_promark/test_synthesis/gen-lab experiments/slt_arctic_demo/test_synthesis/gen-lab/*.lab
