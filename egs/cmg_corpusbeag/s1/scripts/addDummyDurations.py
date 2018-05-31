import sys, io, glob

indir = sys.argv[1]

files = glob.glob(indir+"/*.lab")

for filename in files:
    print("File: %s" % filename)
    infh = io.open(filename, "r", encoding="utf-8")
    lines = infh.readlines()
    infh.close()
    outfh = io.open(filename, "w", encoding="utf-8")
    starttime = 0
    for line in lines:
        lab = line.split()[-1]
        endtime = starttime+50000
        outfh.write("%d %d %s\n" % (starttime,endtime,lab))
        starttime = endtime
    outfh.close()
        
