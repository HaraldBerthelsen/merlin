mkdir -p cmg_corpusbeag_magphase_demo_data/exper
cd cmg_corpusbeag_magphase_demo_data/exper/

mkdir acoustic_model
mkdir duration_model
mkdir test_synthesis

mkdir acoustic_model/conf
mkdir acoustic_model/data
mkdir acoustic_model/data/label_phone_align
mkdir acoustic_model/data/wav

mkdir duration_model/conf
mkdir duration_model/data

mkdir test_synthesis/prompt-lab

cd acoustic_model/data/label_phone_align/
cp ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/htslab/CI0002CMGCorpusBeag_00[012345]*.* .
cp ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/htslab/CI0002CMGCorpusBeag_0060.lab .

cd ../wav/
cp ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/wav/CI0002CMGCorpusBeag_00[012345]*.* .
cp ~/svn/Corpora/ga_MU/cmg/CMGCorpusBeag/wav/CI0002CMGCorpusBeag_0060.wav .

cd ..
ls wav/ | sed 's/.wav//' > file_id_list.scp

cd ..
cd ..
cp acoustic_model/data/file_id_list.scp duration_model/data/

cp acoustic_model/data/label_phone_align/CI0002CMGCorpusBeag_005[6789]* test_synthesis/prompt-lab/
cp acoustic_model/data/label_phone_align/CI0002CMGCorpusBeag_0060.lab test_synthesis/prompt-lab/

cd test_synthesis/
ls prompt-lab/ | sed 's/.lab//' > test_id_list.scp
cd ..
cd ..
