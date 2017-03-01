Download Merlin
---------------

Step 1: git clone https://github.com/CSTR-Edinburgh/merlin.git 

Install tools
-------------

Step 2: cd merlin/tools <br/>
Step 3: ./compile_tools.sh

Demo voice
----------

To run demo voice, please follow below steps:
 
Step 4: cd merlin/egs/slt_arctic/s1 <br/>
Step 5: ./run_demo.sh

Demo voice trains only on 50 utterances and shouldn't take more than 5 min. 

Compare the results in log files to baseline results from demo data in [RESULTS.md](https://github.com/CSTR-Edinburgh/merlin/blob/master/egs/slt_arctic/s1/RESULTS.md)

Full voice
----------

To run full voice, please follow below steps:

Step 6: cd merlin/egs/slt_arctic/s1 <br/>
Step 7: ./run_full_voice.sh

Full voice utilizes the whole arctic data (1132 utterances). The training of the voice approximately takes 1 to 2 hours. 

Compare the results in log files to baseline results from full data in [RESULTS.md](https://github.com/CSTR-Edinburgh/merlin/blob/master/egs/slt_arctic/s1/RESULTS.md)

Generate new sentences
----------------------

To generate new sentences, please follow below steps:

Step 8: Run either demo voice or full voice. <br/>
Step 9: ./merlin_synthesis.sh

###################

promark build:

run_full_voice.sh
cp -r experiments/slt_arctic_full  experiments/slt_arctic_full_promark
make full
run_full_voice_promark.sh

promark test synthesis:
make link to festival dir in <MERLIN>/tools
mkdir -p experiments/slt_arctic_full_promark/test_synthesis/txt

#The file that merlin/festival uses to generate prompt-lab 
echo "This is a test." > experiments/slt_arctic_full_promark/test_synthesis/txt/test.txt

#Really quick-and-dirty way of adding prominence values
#same file name as above but extension .prom
#same text as above but punctuation split
echo "This is a test ." > experiments/slt_arctic_full_promark/test_synthesis/txt/test.prom
#and a line with the same number of tokens, prominence values this time, appended to the same file
echo "150 0 0 20 0" >> experiments/slt_arctic_full_promark/test_synthesis/txt/test.prom

./merlin_synthesis_promark.sh
wavesurfer experiments/slt_arctic_full_promark/test_synthesis/wav/test.wav

##########
promark tobi demo

run_demo.sh
cp -r experiments/slt_arctic_demo experiments/slt_arctic_demo_tobi
make demo_tobi
run_demo_tobi.sh