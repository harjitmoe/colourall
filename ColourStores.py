import os
from ColourDB import get_colourdb_string,ColourDB

dtbs = {}
for f in os.listdir("palettes"):
    p = os.path.join("palettes",f)
    if os.path.isdir(p) or (not f.endswith(".txt")) or f.startswith("info-"):
        continue
    fd = open(p, "rU")
    b = fd.read()
    fd.close()
    name = os.path.splitext(f)[0]
    dtbs[name] = get_colourdb_string(name, b)
    if not dtbs[name]:
        print "Fail",name
        del dtbs[name]
del f; del p; del fd; del b; del name

stad = {}
def stadi(name):
    #Avoid unnecessary forking.
    #Fear not: forest, as the shorter spelling, shall prevail.
    #xkcd's crowdsourced colours use "poop", "poo" and "shit", sometimes unnecessarily forking what is
    #essentially the same colour ("shit" is weighted adversely below, "poo" is favoured anyway as shorter).
    stadn = name.lower().replace("/","").replace(" ","").replace("forrest","forest").replace("shit","poo").replace("poop","poo").replace("cream","creme").replace("gray","grey")
    if stadn not in stad:
        stad[stadn]=[]
    stad[stadn].append(name)
    stad[stadn].append(name.replace("grey","gray"))
    stad[stadn].append(name.replace("gray","grey"))
    return stadn

# Colours which are downright wrong (seemingly a lot of xkcd responders typed "tea" for teal).
too_compromised = [("xkcd","tea")]

def special_update(out,in_,pal=""):
    for key in in_.keys():
        skey = stadi(key)
        if (pal,skey) in too_compromised:
            return
        #No, don't log Bronze II in the stad dict, just quietly fuse it
        #BronzeIi looks like Bronzeli (ie BronzeLi, bronze-ellie) in the interface.
        if skey == "bronzeii":
            skey = "bronze"
        if (skey[-1] in "0123456789"):
            return #Avoid over-representing x11 for the numbered values (hence they are calculated below)
        if skey in out.keys():
            r1,g1,b1=in_[key]
            r2,g2,b2,ct=out[skey]
            out[skey]=((r1+r2),(g1+g2),(b1+b2),(ct+1))
        else:
            out[skey]=in_[key]+(1,)

#Fuse databases using standardised names.
unicolour={}
for pal in dtbs:
    special_update(unicolour,dtbs[pal]._ColourDB__byname.copy(),pal)
#Deal with the blood vs. blood red etc cases.
for name in unicolour:
    if ("gray" in name) or ("grey" in name):
        continue
    for name2 in unicolour:
        if name2 in ("black","white"):
            continue
        if name2 == name:
            continue #don't waste your time.
        if name2 in name: #i.e. name2 shorter.
            r,g,b,ct = unicolour[name]
            r2,g2,b2,ct2 = unicolour[name2]
            #Differences by cross-multiplication ("kiss and smile")
            r3 = (r*ct2) - (r2*ct)
            g3 = (g*ct2) - (g2*ct)
            b3 = (b*ct2) - (b2*ct)
            ct3 = float(ct*ct2)
            #Pythagoration
            magna = (r3**2 + g3**2 + b3**2)**0.5
            if (magna/ct3)<35:
                print "fusing",name,name2
                unicolour[name2] = (r+r2,g+g2,b+b2,ct+ct2)
                stad[name2].append(name)
                stad[name2].extend(stad[name])
                stad[name] = stad[name2] #Note multi-ref mutable
#Add unstandardised names.
for stadn in stad:
    for name in stad[stadn]:
        if stadn in unicolour:
            unicolour[name]=unicolour[stadn]
#Finalise mean averages.
for name in unicolour.copy():
    r,g,b,ct = unicolour[name]
    r = int((r/float(ct))+0.5)
    g = int((g/float(ct))+0.5)
    b = int((b/float(ct))+0.5)
    unicolour[name]=(r,g,b)

#Calculate numbered values
increment_grey = 255/100.0
for inc in range(101):
    rinc = int((inc*increment_grey)+0.5)
    unicolour["Grey%d"%inc] = unicolour["Gray%d"%inc] = (rinc,rinc,rinc)
stata = (None,255,238,205,139)
for col in unicolour.copy():
    col = col.lower()
    if ("grey" in col.lower()) or ("gray" in col.lower()) or col.lower().endswith("white") or col.lower().endswith("black") or col.lower().startswith("light") or col.lower().startswith("bright") or col.lower().startswith("medium") or col.lower().startswith("dark") or col.lower().startswith("dim"):
        continue
    r,g,b = unicolour[col]
    if r==g==b==0:
        continue #/0 error
    v = float(max(r,g,b))
    for n,tv in enumerate(stata):
        if tv == None:
            continue
        numname = col + ("%d"%n)
        numname2 = col + (" %d"%n)
        scalefactor = tv/v
        unicolour[numname2] = (int(r*scalefactor+0.5),int(g*scalefactor+0.5),int(b*scalefactor+0.5))
        if " " not in numname:
            unicolour[numname] = (int(r*scalefactor+0.5),int(g*scalefactor+0.5),int(b*scalefactor+0.5))

#Add camel names
CamelHelper={}
for i in unicolour.keys():
    if " " in i:
        CamelHelper[i.replace(" ","").lower()]=i
def cptlz(s):
    return s[0].upper()+s[1:].lower()
for i in unicolour.keys():
    #Add spaces to numbered names
    nonumber=i.rstrip("0123456789")
    number=i[len(nonumber):]
    if number and (nonumber in CamelHelper):
        i2=CamelHelper[nonumber.lower()]+" "+number
        unicolour[i2]=unicolour[i]
        i=i2
    #Camelize
    j=i.replace("-"," ").replace("/"," ").split()
    j=map(lambda s:cptlz(s),j)
    j="".join(j)
    unicolour[j]=unicolour[i]
    if j.lower()!=i:
        unicolour[j.lower()]=unicolour[j] #Just In Case
for j in unicolour.keys():
    if "'" in j:
        unicolour[j.replace("'","")]=unicolour[j]

#class alertah(dict):
#   def __getitem__(self,n):
#       if n in self.keys():
#           return dict.__getitem__(self,n)
#       else:
#           print "KLAXON!!!!",n
#           return (0,0,0)
#unicolour=alertah(unicolour)

def count_caps_and_apostrophes(str):
    caps=0
    for cap in "ABCDEFGHIJKLMNOPQRSTUVWXYZ'":
        caps+=str.count(cap)
    return caps

def filter_aliases(truename,aliases):
    """Remove overdefinitions (in a case insensitive world) from aliases"""
    done_lowercase=[]
    got={}
    for j in aliases:
        if j.lower() in done_lowercase:
            got[j.lower()].append(j)
        elif j.lower()==truename.lower():
            pass
        else:
            done_lowercase.append(j.lower())
            got[j.lower()]=[j]
    aliases2=[]
    for nameset in got.values():
        mostcaps=0
        mostcapsname=nameset[0] #Default to an arbitary one
        for i in nameset:
            i_caps=count_caps_and_apostrophes(i)
            if i_caps>mostcaps:
                mostcaps=i_caps
                mostcapsname=i
        aliases2.append(mostcapsname)
    return truename,aliases2

def get_priority(name):
    #Would this be described as bayesian?
    priority=0
    priority-=len(name)
    priority+=count_caps_and_apostrophes(name)
    if "gray" in name.lower():
        priority-=210
    if "shit" in name.lower():
        priority-=300
    if name[-1] in "0123456789 ":
        priority-=200
    return priority

class DictColourDB(ColourDB):
    def __init__(self,byname):
        #In DictColourDB not ColourDB so names must be premangled
        self._ColourDB__byname=byname
        byrgb1={}
        for i in byname.keys():
            if byname[i] in byrgb1.keys():
                byrgb1[byname[i]].append(i)
            else:
                byrgb1[byname[i]] = [i]
        byrgb={}
        for i in byrgb1.keys():
            aliases=byrgb1[i]
            truename=None
            abort=False
            aliases=filter_aliases("",aliases)[1]
            shortlist=[]
            for j in aliases:
                if j[0].isupper():
                    shortlist.append(j)
            if not shortlist:
                #print aliases
                shortlist=list(aliases)
            shortlist.sort(key=get_priority,reverse=True)
            truename=shortlist[0]
            #print truename,aliases,shortlist
            aliases.remove(truename)
            byrgb[i]=(truename,aliases)
        self._ColourDB__byrgb=byrgb
        self._ColourDB__allnames=None
        self._ColourDB__name="palettes/(Internal)"

unicolour=DictColourDB(unicolour)
