

#python scripts/genAbairXmlFiles.py $inp_txt ${out_dir}/$file_id_scp ${out_dir}/abair_xml


import sys, os, glob
import collections


def readtext(fname):
    f = open(fname, 'r')
    data = f.read()
    data = data.strip(' \n')
    f.close()
    return data

def create_dictionary_from_txt_dir(txt_dir):
    utt_text = {}
    textfiles = glob.glob(txt_dir + '/*.txt')

    num_of_files = len(textfiles)

    for i in range(num_of_files):
        textfile = textfiles[i]
        junk,filename = os.path.split(textfile)
        filename = filename.split('.')[0]

        text = readtext(textfile)
        utt_text[filename] = text

    return utt_text

def create_dictionary_from_txt_file(txt_file):
    utt_text = {}
    in_f = open(txt_file, 'r')
    for newline in in_f.readlines():
        newline = newline.strip()
        newline = newline.replace('(', '')
        newline = newline.replace(')', '')

        text_parts = newline.split()
        filename = text_parts[0]

        text = ' '.join(text_parts[1:])
        text = text[1:-1] ## remove begining and end double quotes

        utt_text[filename] = text

    return utt_text

if __name__ == "__main__":

    if len(sys.argv)!=4:
        print('Usage: python genAbairXmlFiles.py <in_txt_dir/in_txt_file> <out_file_id_list> <out_xml_dir>')
        sys.exit(1)

    out_id_file  = sys.argv[2]
    out_xml_dir  = sys.argv[3]

    if not os.path.exists(out_xml_dir):
        os.makedirs(out_xml_dir)

    if os.path.isdir(sys.argv[1]):
        print("creating Abair xml files from text directory")
        in_txt_dir = sys.argv[1]
        utt_text   = create_dictionary_from_txt_dir(in_txt_dir)

    elif os.path.isfile(sys.argv[1]):
        print("creating Abair xml files from text file")
        in_txt_file = sys.argv[1]
        utt_text    = create_dictionary_from_txt_file(in_txt_file)

    sorted_utt_text = collections.OrderedDict(sorted(utt_text.items()))

    out_fid = open(out_id_file, 'w')

    ### if you want to use a particular voice
    #out_f1.write("(voice_cstr_edi_fls_multisyn)\n")

    for utt_name, sentence in sorted_utt_text.items():
        out_xml_file_name = os.path.join(out_xml_dir, utt_name+'.xml')
        sentence = sentence.replace('"', '\\"')
        #Run Abair command
        cmd = "python ~/svn/Software/Abair/abair -t textproc %s > %s" % (sentence, out_xml_file_name)
        print("Running command: %s" % cmd)
        os.system(cmd)

        #out_xml.write("(utt.save (utt.synth (Utterance Text \""+sentence+"\" )) \""+out_file_name+"\")\n")
        out_fid.write(utt_name+"\n")

    out_fid.close()
