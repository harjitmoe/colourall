"""Colour Database.

This file contains one class, called ColourDB, and several utility functions.
The class must be instantiated by the get_colourdb() function in this file,
passing it a filename to read a database out of.

The get_colourdb() function will try to examine the file to figure out what the
format of the file is.  If it can't figure out the file format, or it has
trouble reading the file, None is returned.  You can pass get_colourdb() an
optional filetype argument.

Supporte file types are:

    X_RGB_TXT -- X Consortium rgb.txt format files.  Three columns of numbers
                 from 0 .. 255 separated by whitespace.  Arbitrary trailing
                 columns used as the colour name.

The utility functions are useful for converting between the various expected
colour formats, and for calculating other colour values.

"""

import sys
import re
from types import *
import operator

class BadColour(Exception):
    pass

DEFAULT_DB = None
SPACE = ' '
COMMASPACE = ', '



# generic class
class ColourDB:
    def __init__(self, fp):
        lineno = 2
        self.__name = fp.name
        # Maintain several dictionaries for indexing into the colour database.
        # Note that while Tk supports RGB intensities of 4, 8, 12, or 16 bits,
        # for now we only support 8 bit intensities.  At least on OpenWindows,
        # all intensities in the /usr/openwin/lib/rgb.txt file are 8-bit
        #
        # key is (red, green, blue) tuple, value is (name, [aliases])
        self.__byrgb = {}
        # key is name, value is (red, green, blue)
        self.__byname = {}
        # all unique names (non-aliases).  built-on demand
        self.__allnames = None
        while 1:
            line = fp.readline()
            if not line:
                break
            # get this compiled regular expression from derived class
            mo = self._re.match(line)
            if not mo:
                sys.stderr.write('Error in '+repr(fp.name)+' line '+repr(lineno)+'\n')
                lineno = lineno + 1
                continue
            # extract the red, green, blue, and name
            red, green, blue = self._extractrgb(mo)
            name = self._extractname(mo)
            keyname = name.lower()
            # BAW: for now the `name' is just the last named colour with the
            # rgb values we find.  Later, we might want to make the two word
            # version the `name', or the CapitalizedVersion, etc.
            key = (red, green, blue)
            foundname, aliases = self.__byrgb.get(key, (name, []))
            if foundname != name and foundname not in aliases:
                aliases.append(foundname)
            self.__byrgb[key] = (name, aliases)
            # add to byname lookup
            self.__byname[keyname] = key
            lineno = lineno + 1

    # override in derived classes
    def _extractrgb(self, mo):
        return map(int,mo.group('red', 'green', 'blue'))

    def _extractname(self, mo):
        return mo.group('name')

    def filename(self):
        return self.__name

    def find_byrgb(self, rgbtuple):
        """Return name for rgbtuple"""
        try:
            return self.__byrgb[rgbtuple]
        except KeyError:
            raise BadColour(rgbtuple)

    def find_byname(self, name):
        """Return (red, green, blue) for name"""
        name = name.lower()
        try:
            return self.__byname[name]
        except KeyError:
            if name=="grey":
                return self.find_byname("gray")
            raise BadColour(name)

    def nearest(self, red, green, blue):
        """Return the name of colour nearest (red, green, blue)"""
        # BAW: should we use Voronoi diagrams, Delaunay triangulation, or
        # octree for speeding up the locating of nearest point?  Exhaustive
        # search is inefficient, but seems fast enough.
        nearest = -1
        nearest_name = ''
        for name, aliases in self.__byrgb.values():
            r, g, b = self.__byname[name.lower()]
            rdelta = red - r
            gdelta = green - g
            bdelta = blue - b
            distance = rdelta * rdelta + gdelta * gdelta + bdelta * bdelta
            if nearest == -1 or distance < nearest:
                nearest = distance
                nearest_name = name
        return nearest_name

    def nearests(self, red, green, blue):
        """Return the names of colours equidistantly nearest (red, green, blue)"""
        # BAW: should we use Voronoi diagrams, Delaunay triangulation, or
        # octree for speeding up the locating of nearest point?  Exhaustive
        # search is inefficient, but seems fast enough.
        nearest = -1
        nearest_name = ''
        others=[]
        for name, aliases in self.__byrgb.values():
            r, g, b = self.__byname[name.lower()]
            rdelta = red - r
            gdelta = green - g
            bdelta = blue - b
            distance = rdelta * rdelta + gdelta * gdelta + bdelta * bdelta
            if nearest == -1 or distance < nearest:
                nearest = distance
                nearest_name = name
                others = []
            elif distance == nearest:
                others.append(name)
        return [nearest_name]+others

    def unique_names(self,mode="alphabet"):
        # sorted
        if not self.__allnames:
            self.__allnames=BadColour()
        if not hasattr(self.__allnames,mode):
            self.__allnames.__dict__["mode"] = []
            for name, aliases in self.__byrgb.values():
                self.__allnames.__dict__["mode"].append(name)
            
            if mode.lower()=="alphabet":
                # sort irregardless of case
                def my_cmp(n1, n2):
                    v1,v2=n1.lower(),n2.lower()
                    return (v1 > v2) - (v1 < v2)
            else:
                def my_cmp(n1,n2,self=self,mode=mode):
                    r1,g1,b1=self.find_byname(n1)
                    l1=r1*0.299+g1*0.587+b1*0.144
                    r2,g2,b2=self.find_byname(n2)
                    l2=r2*0.299+g2*0.587+b2*0.144
                    if mode.lower()=="luma":
                        v1,v2=l1,l2
                        o1,o2= 0, 0
                    elif mode.lower()=="red":
                        v1,v2=r1,r2
                        o1,o2=g1+b1, g2+b2
                    elif mode.lower()=="green":
                        v1,v2=g1,g2
                        o1,o2=r1+b1, r2+b2
                    elif mode.lower()=="blue":
                        v1,v2=b1,b2
                        o1,o2=r1+g1, r2+g2
                    elif mode.lower()=="chroma":
                        #u1= - 0.169*r1 - 0.331*g1 + 0.500*b1
                        #u2= - 0.169*r2 - 0.331*g2 + 0.500*b2
                        #_v1=+ 0.500*r1 - 0.419*g1 - 0.081*b1
                        #_v2=+ 0.500*r2 - 0.419*g2 - 0.081*b2
                        #import math
                        #v1=math.hypot(u1,_v1)
                        #v2=math.hypot(u2,_v2)
                        v1=(max(r1,l1)-min(r1,l1))+(max(g1,l1)-min(g1,l1))+(max(b1,l1)-min(b1,l1))
                        v2=(max(r2,l2)-min(r2,l2))+(max(g2,l2)-min(g2,l2))+(max(b2,l2)-min(b2,l2))
                        o1,o2=-l1,-l2
                    else:
                        v1,v2=l1,l2
                        o1,o2= 0, 0
                    if v1==v2:
                        v1,v2=-o1,-o2
                    return (v1 > v2) - (v1 < v2)
            try:
                sorted
            except NameError:
                args,kwargs=(my_cmp,),{}
            else:
                args,kwargs=(),{"key":cmp_to_key(my_cmp)}
            self.__allnames.__dict__["mode"].sort(*args,**kwargs)
        return self.__allnames.__dict__["mode"]

    def aliases_of(self, red, green, blue):
        try:
            name, aliases = self.__byrgb[(red, green, blue)]
        except KeyError:
            raise BadColour((red, green, blue))
        return [name] + aliases


def cmp_to_key(cmper):
    print "CMPer to KEYer"
    class keyer(object):
        def __init__(self, o, *args):
            self.o = o
        def __lt__(a, b):
            return cmper(a.o, b.o) < 0
        def __gt__(a, b):
            return cmper(a.o, b.o) > 0
        def __eq__(a, b):
            return cmper(a.o, b.o) == 0
        def __le__(a, b):
            return cmper(a.o, b.o) <= 0
        def __ge__(a, b):
            return cmper(a.o, b.o) >= 0
        def __ne__(a, b):
            return cmper(a.o, b.o) != 0
    return keyer

class RGBToNameColourDB(ColourDB):
    _re = re.compile(
        '\s*(?P<red>\d+)\s+(?P<green>\d+)\s+(?P<blue>\d+)\s+(?P<name>.*)')

class NameToHexDB(ColourDB):
    _re = re.compile('(?P<name>(.+))\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo):
        return rrggbb_to_triplet(mo.group('hexrgb'))

    def _extractname(self, mo):
        return mo.group('name').strip()

class HexToNameDB(NameToHexDB):
    _re = re.compile('(?P<hexrgb>#[0-9a-fA-F]{6})\s+(?P<name>(.+))')

class CrayolaDB(NameToHexDB):
    _re = re.compile('[0123456789]+\s+(?P<name>(.+?))\s+(?P<hexrgb>#[0-9a-fA-F]{6})')

class NamelessHexDB(ColourDB):
    _re = re.compile('(?P<hexrgb>#[0-9a-fA-F]{6})')

    def _extractrgb(self, mo):
        return rrggbb_to_triplet(mo.group('hexrgb'))

    def _extractname(self, mo):
        return mo.group('hexrgb').upper()



# format is a tuple (RE, CLASS) where RE is a compiled regular
# expression and CLASS is the class to instantiate if a match is found

FILETYPES = [
    (re.compile('Xorg'),                             RGBToNameColourDB),
    (re.compile('XConsortium'),                      RGBToNameColourDB),
    (re.compile('X11[- ]?[sS]tyle'),                 RGBToNameColourDB),
    (re.compile('HTML'),                             NameToHexDB),
    (re.compile('lightlink'),                        NameToHexDB),
    (re.compile('[nN]ame[- ]?[tT]o[- ]?[hH]ex'),     NameToHexDB),
    (re.compile('[hH]ex[- ]?[tT]o[- ]?[nN]ame'),     HexToNameDB),
    (re.compile('Websafe'),                          NamelessHexDB),
    (re.compile('[hH]ex[- ]?[vV]alues[- ]?[oO]nly'), NamelessHexDB),
    (re.compile('[cC]rayola'),                       CrayolaDB),
    ]

def get_colourdb(file, filetype=None):
    fp = open(file)
    return _get_colourdb(fp, filetype)

def get_colourdb_string(name, file, filetype=None):
    import StringIO
    fp = StringIO.StringIO(file)
    fp.name="palettes/<"+name+">"
    return _get_colourdb(fp, filetype)

def _get_colourdb(fp, filetype):
    colourdb = None
    try:
        line = fp.readline()
        if not line:
            return None
        # try to determine the type of RGB file it is
        if filetype is None:
            filetypes = FILETYPES
        else:
            filetypes = [filetype]
        for typere, class_ in filetypes:
            mo = typere.search(line)
            if mo:
                break
        else:
            # no matching type
            return None
        # we know the type and the class to grok the type, so suck it in
        colourdb = class_(fp)
    finally:
        fp.close()
    # save a global copy
    global DEFAULT_DB
    DEFAULT_DB = colourdb
    return colourdb



_namedict = {}

def rrggbb_to_triplet(colour):
    """Converts a #rrggbb colour to the tuple (red, green, blue)."""
    rgbtuple = _namedict.get(colour)
    if rgbtuple is None:
        if colour[0] != '#':
            raise BadColour(colour)
        red = colour[1:3]
        green = colour[3:5]
        blue = colour[5:7]
        rgbtuple = int(red, 16), int(green, 16), int(blue, 16)
        _namedict[colour] = rgbtuple
    return rgbtuple


_tripdict = {}
def triplet_to_rrggbb(rgbtuple):
    """Converts a (red, green, blue) tuple to #rrggbb."""
    global _tripdict
    hexname = _tripdict.get(rgbtuple)
    if hexname is None:
        hexname = '#%02x%02x%02x' % rgbtuple
        _tripdict[rgbtuple] = hexname
    return hexname


_maxtuple = (256.0,) * 3
def triplet_to_fractional_rgb(rgbtuple):
    return map(operator.__div__, rgbtuple, _maxtuple)


def triplet_to_brightness(rgbtuple):
    # return the brightness (grey level) along the scale 0.0==black to
    # 1.0==white
    r = 0.299
    g = 0.587
    b = 0.114
    return r*rgbtuple[0] + g*rgbtuple[1] + b*rgbtuple[2]



if __name__ == '__main__':
    colourdb = get_colourdb('/usr/openwin/lib/rgb.txt')
    if not colourdb:
        print 'No parseable colour database found'
        sys.exit(1)
    # on my system, this colour matches exactly
    target = 'navy'
    red, green, blue = rgbtuple = colourdb.find_byname(target)
    print target, ':', red, green, blue, triplet_to_rrggbb(rgbtuple)
    name, aliases = colourdb.find_byrgb(rgbtuple)
    print 'name:', name, 'aliases:', COMMASPACE.join(aliases)
    r, g, b = (1, 1, 128)                         # nearest to navy
    r, g, b = (145, 238, 144)                     # nearest to lightgreen
    r, g, b = (255, 251, 250)                     # snow
    print 'finding nearest to', target, '...'
    import time
    t0 = time.time()
    nearest = colourdb.nearest(r, g, b)
    t1 = time.time()
    print 'found nearest colour', nearest, 'in', t1-t0, 'seconds'
    # dump the database
    for n in colourdb.unique_names():
        r, g, b = colourdb.find_byname(n)
        aliases = colourdb.aliases_of(r, g, b)
        print '%20s: (%3d/%3d/%3d) == %s' % (n, r, g, b,
                                             SPACE.join(aliases[1:]))
