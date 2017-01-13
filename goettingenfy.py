#!/usr/bin/env python
# vim: set fileencoding=UTF8 :

# Files and directories to be searched

import glob, os, sys, getopt, re, collections

reload(sys)
sys.setdefaultencoding('utf-8')

base = './src'
# Where to look for replacements
places = ['lib', 'fixes', 'config*', 'public', 'views']

# Function needed to allow regular expression patterns in the replacement list
def r (pattern):
    return re.compile(pattern)

replacements = collections.OrderedDict()

# What should be replaced
# Use Python raw strings (r'') to make sure that strings with backslashes are not interpreted as escape sequences
# Use the function r() to wrap up things that are regular expressions

replacements[r'\\line PUB: {\\field{\\*\\fldinst HYPERLINK http://pub.uni-bielefeld.de/$bag/$pub->{_id}}{\\fldrslt http://pub.uni-bielefeld.de/$bag/$pub->{_id}}}'] = ''
replacements[r'\\line PhilLister: {\\field{\\*\\fldinst HYPERLINK http://phillister.ub.uni-bielefeld.de/$bag/$ext->{phillister}}{\\fldrslt $ext->{phillister}}}'] = ''
replacements[r'\\line PUB: {\\field{\\*\\fldinst HYPERLINK http://pub.uni-bielefeld.de/$bag/$pub->{_id}}{\\fldrslt http://pub.uni-bielefeld.de/$bag/$pub->{_id}}}'] = ''
replacements[r'{\\field{\\*\\fldinst HYPERLINK http://pub.uni-bielefeld.de/$bag/$pub->{_id}}{\\fldrslt '] = ''
replacements['vitali.peil@uni-bielefeld.de'] = 'beucke@sub.uni-goettingen.de'
replacements['https://pub.uni-bielefeld.de/oai'] = 'http://pub-dev.sub.uni-goettingen.de/oai'
replacements['PUB - Publications at Bielefeld University'] = 'GRO - Göttingen Research Online'
replacements['publikationsdienste.ub@uni-bielefeld.de'] = 'epu@sub.uni-goettingen.de'
replacements['https://ekvv.uni-bielefeld.de/pers_publ/publ/PersonDetail.jsp?personId='] = ''
replacements['oai:pub.uni-bielefeld.de:1585315'] = 'oai:pub-dev.sub.uni-goettingen.de:2737399'
replacements['https://pub.uni-bielefeld.de'] = 'https://www.sub.uni-goettingen.de'
replacements['pub.uni-bielefeld.de'] = 'pub-dev.sub.uni-goettingen.de'
replacements['LibreCat University'] = 'Göttingen University'
replacements['Bielefeld University'] = 'Göttingen University'
replacements['Universität Bielefeld'] = 'Georg-August-Universität Göttingen'
replacements['Universitätsbibliothek Bielefeld'] = 'Niedersächsische Staats- und Universitätsbibliothek Göttingen'
replacements['Universitätsstr. 25, 33615 Bielefeld'] = 'Platz der Göttinger Sieben 1, 37073 Göttingen'
replacements['Bielefeld'] = 'Göttingen'
replacements[r('PUB([^\w])')] = r'GRO\1'
replacements['L6000-0538'] = ''
replacements['24060-6'] = '2020450-4'

#List to count if all replacements have been made
replaced = []

def find_files (files):
    ret = []
    for file in files:
        ret.extend(glob.glob(file))
    return ret

def change_file (file, edit, verbose):
    content = ''
    with open (file, 'rt') as infile:
        linenr = 0
        result = False
        for line in infile:
            linenr += 1
            position = "File: " + file + ":" + str(linenr) + ": "
            for fro, to in replacements.items():
                if isinstance(fro, str):
                    search = fro
                    newline = line.replace(fro, to)
                elif isinstance(fro, re._pattern_type):
                    search = fro.pattern
                    regex = fro
                    newline = regex.sub(to, line)
                if line != newline:
                    print position + "changed \"" + search + "\" "
                    if replacements[fro] == '':
                        print "(Warning, no replacement for  \"" + search+ "\")"
                    result = True
                    if verbose:
                        print "Change \"" + line + "\" to \"" + newline + "\"" 
                    line = newline
                    if fro not in replaced:
                        replaced.append(fro)
            content = content + newline
    if edit == True:
        resultfile = file + ".new"
    else:
        resultfile = file
    if result:
        with open(resultfile, 'w') as new_file:
            new_file.write(content)
        print "File " + resultfile + " written"
            
def main(argv):
    help = 'goettingenfy.py -s <srcdir>'
    test = False
    verbose = False
    try:
       opts, args = getopt.getopt(argv,"hvts:",["srcdir=",])
    except getopt.GetoptError:
       print help
       sys.exit(2)
 
    for opt, arg in opts:
      if opt == '-h':
         print help
         sys.exit()
      elif opt in ("-s", "--srcdir"):
         srcdir = arg
      elif opt == '-t':
         test = True
      elif opt == '-v':
         verbose = True
    os.chdir(srcdir)
    for searchroot in find_files(places):
        if os.path.isfile(searchroot):
            change_file(searchroot, test, verbose)
        elif os.path.isdir(searchroot):
            for root, dirs, files in os.walk(searchroot):
                for file in files:
                    change_file(os.path.join(root, file), test, verbose)
    for key in replacements.keys():
        if key not in replaced:
            if isinstance(key, str):
                r = key
            elif isinstance(key, re._pattern_type):
                r = key.pattern
            print "Warning: \"" + r + "\" was not replaced!"

if __name__ == "__main__":
   main(sys.argv[1:])