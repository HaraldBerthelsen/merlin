#Look in input dir for .txt files
#If there is a corresponding .prom file, open it and split to tokens, add prom value at end of label line in output dir

import sys, glob, re, os.path

def main():
    global indir, promptlabdir
    
    indir = sys.argv[1]
    promptlabdir = sys.argv[2]
    
    txtfiles = glob.glob("%s/*.txt" % indir)

    for txtfile in txtfiles:
        addProm(txtfile)
        # try:
        #     addProm(txtfile)
        # except:
        #     print("FAILED addProm(%s)" % txtfile)
        #     sys.exit(1)


def addProm(txtfile):
    print("TXT %s" % txtfile)
    basename = os.path.basename(os.path.splitext(txtfile)[0])
    print("BASENAME: %s" % basename)
    promfile = os.path.join(indir,basename+".prom")
    if not os.path.isfile(promfile):
        print("NO PROMFILE")
        return

    fh = open(promfile)
    promlines = fh.readlines()
    fh.close()

    texttokens = promlines[0].strip().split()
    promvalues = promlines[1].strip().split()

    if len(texttokens) > len(promvalues):
        print("ERROR (text tokens and prominence values don't match in %s):\n%s\n%s" % (promfile,texttokens,promvalues))
        sys.exit(1)


    #Add the initial silence token to texttokens and promvalues
    #texttokens.insert(0, "initial_silence")
    #promvalues.insert(0, "0")
    
    #Add the final silence token to texttokens and promvalues
    #IF the last token isn't punctuation
    #if not re.match("[.,?!:;]", texttokens[-1]):
    #texttokens.append("final_silence")
    #promvalues.append("0")

    #The "nr" is x if the token is a silence
    
        
    #Now read prompt-lab, append prom values, and print it back
    promptlabfile = os.path.join(promptlabdir,basename+".lab")
    if not os.path.isfile(promfile):
        print("ERROR: %s missing" % promptlabfile)
        sys.exit(1)
    pfh = open(promptlabfile)
    pl_lines = pfh.readlines()
    pfh.close()
    new_pl_lines = []
    prev = 0
    i = -1
    for pl_line in pl_lines:
        pl_line = pl_line.strip()

        #OLD#find when a new token begins
        #m = re.search("-([^+]+)\+.+\@([0-9x]+)\+", pl_line)

        #NEW find when a syllable begins
        #Between & and - in the label file
        m = re.search("-([^+]+)\+.+\&([0-9x]+)\-", pl_line)
        
        symbol = m.group(1)
        syllnr = m.group(2)
        if syllnr != prev:
            prev = syllnr
            if syllnr == "x":
                promvalue = "0"
            else:
                i += 1
                if len(promvalues)-1 < i:
                    print("ERROR: not enough promvalues in %s" % promfile)
                    sys.exit(1)
                promvalue = promvalues[i]
            print("NEW SYLLABLE NR: %s, index: %d" % (syllnr, i))

        if syllnr == "x":
            promvalue = "0"
        else:
            if len(promvalues)-1 < i:
                print("ERROR: not enough promvalues in %s" % promfile)
                sys.exit(1)
            promvalue = promvalues[i]

            
        #add prom before state if it exists
        m2 = re.search("^(.+)(\[[0-9]+\])$", pl_line)
        if m2:
            first = m2.group(1)
            last = m2.group(2)
            print("Adding syllable %d: promvalue %s to label file, symbol: %s" % (i,promvalue, symbol))
            new_pl_line = first+"/K:"+promvalue+last
        else:
            new_pl_line = pl_line+"/K:"+promvalue
        #print(new_pl_line)
        
        new_pl_lines.append(new_pl_line)

    if len(promvalues) > i+1:
        print("ERROR (text tokens and prominence values don't match in %s):\n%s\n%s\npromvalues: %d, nr of tokens: %d" % (promfile,texttokens,promvalues, len(promvalues), i))
        sys.exit(1)
        
    new_pl_data = "\n".join(new_pl_lines)

    #print(new_pl_data)
    
    out = open(promptlabfile,"w")
    out.write(new_pl_data)
    out.close()


    
    
    

if __name__ == "__main__":
    main()
