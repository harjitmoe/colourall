#!/usr/bin/python -i

cache={}

clashes=[]

def compprep(n):
	return n.lower().replace("-","").replace(" ","").replace("_","").replace("grey","gray").replace("navyblue","navy")

def read(file):
	f=open(file+".txt","rU")
	b=f.read().split("\n")
	f.close()
	d={}
	d2={}
	for line in b:
		if not line.strip():
			continue
		if line[0] in "!#":
			continue
		line=line.replace("\t"," ").strip()
		while "  " in line:
			line=line.replace("  "," ")
		if line[0].isdigit():
			name=line.split()
			r=name.pop(0)
			g=name.pop(0)
			b=name.pop(0)
			name=" ".join(name)
		else:
			#print line
			name=line.split()
			hex=name.pop()
			name=" ".join(name)
			hex=hex[1:]
			r="0x"+hex[:2]
			g="0x"+hex[2:4]
			b="0x"+hex[4:6]
		d[name]=eval(r),eval(g),eval(b)
		d2[compprep(name)]=eval(r),eval(g),eval(b)
		if compprep(name) in cache.keys() and cache[compprep(name)]!=d[name]:
			if compprep(name) not in clashes:
				clashes.append(compprep(name))
	globals()[file]=d
	globals()[file+"_cprp"]=d2
	cache.update(d2)

#read("namedcolors")
read("webcolors")
read("html40colors")
read("rgb")

def figure(i,names):
	values={}
	for name,dic in names.items():
		if i in dic.keys():
			t=dic[i]
			if t not in values.keys():
				values[t]=[name]
			else:
				values[t].append(name)
	volues=values.copy()
	for i in values.keys():
		if len(values[i])>1:
			values[i]=", ".join(values[i][:-1])+" and "+values[i][-1]
		else:
			values[i]=values[i][0]
	res=sorted(zip(values.values(),values.keys()))
	res2=sorted(zip(volues.values(),volues.keys()))
	pool={}
	for i in volues.values():
		for j in i:
			pool[j]=True
	pool=pool.keys()
	for i,j in res2:
		for k in pool:
			if k not in i:
				if j in names[k].values():
					nk=dict(zip(names[k].values(),names[k].keys()))
					print "-",k,"thinks",j,"is",nk[j]
	return res

print "========================================================="
print "Clashes (generally between web (ie W3C standard) and X11)"
print "========================================================="
print
for i in clashes:
	print i
	print "-"*len(i)
	print
	for a,b in figure(i,{
	    "MSIE":webcolors_cprp,
	    "NS":webcolors_cprp,
	    "W3C":html40colors_cprp,
	    "X11":rgb_cprp,
	    #"http://www.lightlink.com/xine/bells/namedcolors.html":namedcolors_cprp
	    }):
		print "- According to",a,i,"is",b
	print
print "I hear that X11 maroon is known by some as 'rich' maroon for identification"
print

print "================================================"
print "Completely unsupported X Colour names in MSIE/NS"
print "   (apart from the obvious numbered entries)"
print "================================================"
print
for i in rgb_cprp.keys():
	if (i not in webcolors_cprp.keys()) and ("0" not in i)\
                                            and ("1" not in i)\
                                            and ("2" not in i)\
                                            and ("3" not in i)\
                                            and ("4" not in i)\
                                            and ("5" not in i)\
                                            and ("6" not in i)\
                                            and ("7" not in i)\
                                            and ("8" not in i)\
                                            and ("9" not in i):
		print "- "+i
print
print "Completely unsupported means no varient of the name is assigned to any colour"
print "whatsoever"
print

print "======================================="
print "MSIE/NS colours not W3C standard or X11"
print "======================================="
print
for i in webcolors_cprp.keys():
	if (i not in rgb_cprp.keys()) and (i not in html40colors_cprp.keys()):
		print "- "+i
print

