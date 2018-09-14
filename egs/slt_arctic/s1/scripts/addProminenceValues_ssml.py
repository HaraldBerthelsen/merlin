import sys, glob, re, os.path
import lxml.etree as et

def main():
    global indir, promptlabdir
    
    indir = sys.argv[1]
    promptlabdir = sys.argv[2]
    
    txtfiles = glob.glob("%s/*.txt" % indir)

    for txtfile in txtfiles:
        addProm(txtfile)


def addProm(txtfile):
    print("TXT %s" % txtfile)
    basename = os.path.basename(os.path.splitext(txtfile)[0])

    fh = open(txtfile)
    txt = fh.read()
    fh.close()

    promvalues = getPromValues(txt)

    if promvalues:
        promptlabfile = os.path.join(promptlabdir,basename+".lab")
        print("LAB: %s" % promptlabfile)
    
        lab = getLab(promptlabfile)
        lab = addPromValuesToLab(lab, promvalues)
        printLab(promptlabfile, lab)
        

def getPromValues(txt):
    #print("TXT: %s" % txt.strip())

    if ":P" in txt:
        (txttokens,promvalues) = getPromValues_P_notation(txt)
        printPromvalues(txttokens, promvalues)    
        return promvalues
    
    elif "<emphasis" in txt:
        (txttokens,promvalues) = getPromValues_SSML(txt)
        printPromvalues(txttokens, promvalues)    
        return promvalues


def getPromValues_P_notation(txt):
    txt = re.sub("\n", " ", txt.strip())
    txt = re.sub(" +", " ", txt)
    txttokens = []
    promvalues = []
    punct = None
    for token in txt.split(" "):            
        #print("Token: %s" % token)
        m = re.match("^(.+):P([a-z0-9|+=%-]+)([^a-z0-9]+)?$", token)
        if m:
            word = m.group(1)
            pes = m.group(2)
            punct = m.group(3)
            prom = []
            #print("pes: %s" % pes)
            for pe in pes.split("|"):
                m = re.match("^([=+-])([0-9]+|strong|moderate|reduced|keep)(%)?$", pe)
                pm = m.group(1)
                p = m.group(2)
                pc = m.group(3)
                pv = convertPromString(pm,p,pc)
                prom.append(pv)
                
        else:
            prom = ["keep"]
            word = token
            
        promvalues.append(prom)
        if punct:            
            txttokens.append(word+punct)
        else:
            txttokens.append(word)
    return (txttokens, promvalues)
                          
def getPromValues_SSML(ssml):
    txttokens = []
    promvalues = []
    s = et.fromstring(ssml)

    initial_text = s.text
    print("initial_text: %s" % initial_text)
    (txttokens, promvalues) = addKeepTokens(initial_text,txttokens,promvalues)

    
    for e in s.iter("emphasis"):
        print(et.tostring(e))
        (txttokens, promvalues) = addEmphasisTokens(e, txttokens, promvalues)
        print("tail: %s" % e.tail)
        (txttokens, promvalues) = addKeepTokens(e.tail, txttokens, promvalues)
        
    return (txttokens, promvalues)

def addKeepTokens(text, txttokens, promvalues):
    tokens = text.strip().split()
    for token in tokens:
        txttokens.append(token)
        promvalues.append(["keep"])
    return (txttokens, promvalues)

def addEmphasisTokens(e, txttokens, promvalues):

    prom = []
    level = e.attrib["level"]
    for pe in level.split("|"):
        m = re.match("^([=+-])?([0-9]+|strong|moderate|reduced|keep)(%)?$", pe)
        pm = m.group(1)
        p = m.group(2)
        pc = m.group(3)
        pv = convertPromString(pm,p,pc)
        prom.append(pv)
        
    text = e.text
    tokens = text.strip().split()
    for token in tokens:
        txttokens.append(token)
        promvalues.append(prom)
    
    return (txttokens, promvalues)


def convertPromString(pm,p,pc):
    if pm == None:
        pm = "="
        
    if p == "strong":
        pv = ("=", 200, None)
    elif p == "moderate":
        pv = ("=", 50, None)
    elif p == "reduced":
        pv = ("=", 0, None)
    elif p == "keep":
        pv = "keep"

    #Can't subtract more than 100 %
    elif pm == "-" and pc == "%" and int(p) > 100:
        print("Trying to subtract more than 100%%: (%s, %s, %s), changed to 100%%" % (pm,p,pc))
        pv = (pm,100,pc)
        
    else:
        pv = (pm,int(p),pc)
    return pv

def getLab(promptlabfile):
    """Read labfile, split into list of words, which is a list of syllables, which is a list of lablines for each phoneme."""
    
    if not os.path.isfile(promptlabfile):
        print("ERROR: %s missing" % promptlabfile)
        sys.exit(1)
    pfh = open(promptlabfile)
    pl_lines = pfh.readlines()
    pfh.close()

    syll = []
    #word = [syll]
    #lab = [word]
    word = []
    lab = []

    prevwordnr = 0
    prevsyllnr = 0
    prevline = None
    for pl_line in pl_lines:
        pl_line = pl_line.strip()



        if prevline:
            syll.append(prevline)

        
        #word nr between @ and + in the label file
        #syll nr between & and - in the label file
        m = re.search("-([^+]+)\+.+\&([0-9x]+)\-.+\@([0-9x]+)\+", pl_line)
        
        symbol = m.group(1)
        syllnr = m.group(2)
        wordnr = m.group(3)

        #print("symbol: %s" % symbol)

        if wordnr != prevwordnr:
            #print("NEW WORD: %s %s %s" % (symbol, prevwordnr,wordnr))
            prevwordnr = wordnr
            prevsyllnr = syllnr
            if prevline:
                word.append(syll)
                lab.append(word)
                word = []
                syll = []
        elif syllnr != prevsyllnr:
            #print("NEW SYLL: %s %s %s" % (symbol, prevsyllnr, syllnr))
            prevsyllnr = syllnr
            word.append(syll)
            syll = []
        #else:
            #print("same syll: %s %s %s" % (symbol, prevsyllnr, syllnr))

            
        prevline = pl_line

    #Last line
    syll.append(prevline)
    word.append(syll)
    lab.append(word)
            
    return lab

def addPromValuesToLab(lab,promvalues):
    linenr = 0
    i = 0
    newlab = [lab[0]]
    newword = []
    newsyll = []
    for word in lab[1:-1]:
        promword = promvalues[i]
        s = 0
        for syll in word:
            try:
                promsyll = promword[s]
            except:
                #one value for all syllables in word
                pass
            for pl_line in syll:
                linenr += 1
                symbol = re.search("-([^+]+)\+", pl_line).group(1)
                
                #print(promsyll)

                #Get existing K
                m0 = re.search("/K:([0-9]+)", pl_line)
                if m0:
                    prev_promvalue = int(m0.group(1))
                else:
                    prev_promvalue = 0
                    print("WARNING: no K in line\n%s\npromvalue set to 0" % pl_line)
                #remove existing /K:
                pl_line_no_k = re.sub("/K:[0-9]+", "", pl_line)        

                if promsyll == "keep":
                    promvalue = prev_promvalue
                else:
                    (pm,pv,pc) = promsyll
                    #Compute promvalue
                    if pm == "=":
                        if pc == "%":
                            promvalue = prev_promvalue*pv*0.01
                        else:
                            promvalue = pv
                    elif pm == "+":
                        if pc == "%":
                            promvalue = prev_promvalue+prev_promvalue*pv*0.01
                        else:
                            promvalue = prev_promvalue+pv
                    elif pm == "-":
                        if pc == "%":
                            promvalue = prev_promvalue-prev_promvalue*pv*0.01
                        else:
                            promvalue = prev_promvalue-pv
                    else:
                        print("This shouldn't happen..")
                        sys.exit()

                #round..
                promvalue = int(promvalue)

                #TODO better print..
                print("Line %3d, symbol %3s:\t%3d %s\t->\t%d" % (linenr,symbol,prev_promvalue, promsyll, promvalue))
                #print("%d\t->\t%d" % (prev_promvalue,promvalue))
                    
                #add prom before state if it exists
                m = re.search("^(.+)(\[[0-9]+\])$", pl_line_no_k)
                if m:
                    first = m.group(1)
                    last = m.group(2)
                    #print("Adding syllable %d-%d: promvalue %s to label file" % (i, s,promvalue))
                    new_pl_line = first+"/K:"+str(promvalue)+last
                else:
                    #print("Adding syllable %d-%d: promvalue %s to label file" % (i, s,promvalue))
                    new_pl_line = pl_line_no_k+"/K:"+str(promvalue)
                newsyll.append(new_pl_line)

            s += 1
            newword.append(newsyll)
            newsyll = []
        i += 1
        newlab.append(newword)
        newword = []
        
    #new_pl_data = "\n".join(new_pl_lines)
    newlab.append(lab[-1])
    return newlab

    
def printLab(promptlabfile, lab):
    
    out = open(promptlabfile,"w")
    for word in lab:
        for syll in word:
            for phn in syll:
                out.write(phn+"\n")
    out.close()

def debugPrintLab(lab):
    print(lab)

    print("LAB")
    for word in lab:
        print("WORD")
        for syll in word:
            print("SYLL")
            for phn in syll:
                print(phn)

    

def printPromvalues(txttokens, promvalues):    
    i = 0
    while i < len(txttokens):
        print("%s\t%s" % (txttokens[i], promvalues[i]))
        i += 1

    
def testP():
        
    (txttokens, promvalues) = getPromValues_P_notation("""hello:P+20%|-20% this:P-50% is:P=reduced a test:P=200 25""")

    printPromvalues(txttokens, promvalues)    
    
    labfile = "scripts/test_add_prom.lab"
    lab = getLab(labfile)


    #debugPrintLab(lab)

    
    lab = addPromValuesToLab(lab, promvalues)
    debugPrintLab(lab)
    #normally don't overwrite the test file..
    #printLab(labfile, lab)
    


def testSsml():
        
    (txttokens, promvalues) = getPromValues_SSML("""<speak> <emphasis level="+50%|-20%"> hello </emphasis> <emphasis level="-50%"> this is </emphasis> a <emphasis level="200"> test </emphasis> </speak>""")

    printPromvalues(txttokens, promvalues)    
    
    labfile = "scripts/test_add_prom.lab"
    lab = getLab(labfile)
    debugPrintLab(lab)

    
    lab = addPromValuesToLab(lab, promvalues)
    debugPrintLab(lab)
    #normally don't overwrite the test file..
    #printLab(labfile, lab)
    


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        testP()
        testSsml()

