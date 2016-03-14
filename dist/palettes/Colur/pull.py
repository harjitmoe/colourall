#XXX Multiline colour support (this does happen with B (biological) but to be fair the general audience does not use geni as colour names)

#The Python<=1.4 one, not to be confused with the high-level-low-usabilty "regex" or its successer "re"
#This is an anachronism, I got this from the 1.4 source tree and compiled 2.4 regex as a backend
import regexp

main_re=regexp.compile('^<tr><td>([][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 (){}]+)</td>(.*)</tr>')

#If colour number ends with a minus it probably means it is almost certaily a typo
#If colour number ends with + it means a typo or omission fix(?)
#For example quince yellow: the author of the table has wisely decided the Prussian Blue/Slate Grey
#187 is a typo (marked with -) and made own contribution 87 (a yellow-brown) marked with +
col_re=regexp.compile('<td( width="5%")? title="[0123456789]+" style="background-color:#?([0123456789ABCDEF]+)(; color:#FFF)?">[0123456789]*[^-]</[tT][dD]>')

d={}

def extract(colours):
	rgbs=set()
	while 1:
		match=col_re.match(colours)
		if not match:
			break
		rgb=colours[match[2][0]:match[2][1]]
		rgbs.add(rgb)
		colours=colours[match[0][1]:]
	return frozenset(rgbs)

for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
	for line in open("ISCC-NBS "+letter+".htm","rU").readlines():
		match=main_re.match(line) #Equivalent to more modern RE modules' "search"
		if match:
			name=line[match[1][0]:match[1][1]]
			col =line[match[2][0]:match[2][1]]
			if name in d.keys():
				d[name]|=extract(col)
			else:
				d[name]=extract(col)

#Dictionary Copyright (c) 2004-2005 Voluntocracy. Permission is granted to copy and distribute modified or unmodified versions of this color dictionary provided the copyright notice and this permission notice are preserved on all copies and the entire such work is distributed under the terms of a permission notice identical to this one. 

