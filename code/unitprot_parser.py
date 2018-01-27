
import pandas as pd
from pandas import DataFrame
import os
import sys
import gzip
from io import StringIO

VERBOSE = False

# extract the data from a .gz file, assuming it contains a txt file and returns an array of lines
def extract(filepath):
    if (VERBOSE):
        print("Extracting " + filepath)
        
    f = gzip.open(filepath, 'rb')
    file_content = f.read()
    f.close()
    text = file_content.decode("utf-8")
    #return pd.read_csv(StringIO(text), delimiter="\t")
    return text.split('\n')

# str.split(delimiter) returns also empty elements; this function simply removes them
def split(s, delimiter):
    content = s.split(delimiter)
    return [item for item in content if item]

# This function adds an couple key-value to a dict assuming it associates a key to a list.
# The value is meant to be added to the array, but if the key does not exist, you will need to create the array first. 
# This function creates this array for you if it doesn't exist yet.
def appendToSubArray(di, key, value):
    if not key in di:
        di[key] = []
    di[key].append(value)
    
def fill(s, elems):
    if isinstance(elems, str):
        elems = [elems]
    spacesplit = split(s, ' ')
    for i in range(len(spacesplit)):
        if len(spacesplit[i]) and spacesplit[i][0] == '$':
            ind = int(spacesplit[i][1:])
            if ind - 1 < len(elems) and ind - 1 >= 0:
                spacesplit[i] = str(elems[ind - 1])
    return ' '.join(spacesplit)
   
# # Parsing UnitProt data

# ## Functions to generate queries from data
# 
# The following functions are used in the generation of SQL script from data.
# 
# **toSQLStr** converts a chunk of data (a tuple/list or a single element) to a format suited for an INSERT query.
# The main problem encountered here is that some names may contains single quotes('). SQL allows escaping those by adding an additional quote :
#     'go'el' => 'go''el'

def toSQLStr(tup):
   result = "("
   if type(tup) == str:
       subitem = ""
       for c in tup:
           if c in "'":
               subitem = subitem + "'"
           subitem = subitem + c
       result = result + "'" + subitem + "'"
   elif type(tup) == tuple or type(tup) == list:
       first = True
       for item in tup:
           if not item:
               continue
           if first:
               first = False
           else:
               result = result + ", "
           if type(item) == str:
               subitem = ""
               for c in item:
                   if c in "'":
                       subitem = subitem + "'"
                   subitem = subitem + c
               result = result + "'" + subitem + "'"
           else:
               result = result + str(item)
   return result + ")"


# **writeInsertQuery** generates an INSERT query from the lines given as parameter. 
# It uses the above function to convert those lines of data to a format suitable to SQL.
# The query is written to the file specified by `filepath`.

def writeInsertQuery(table, lines, filepath):
    if len(lines) == 0 or not table or not filepath:
        return
    if (VERBOSE):
        print("Generating INSERT query for " + table)
    with open(filepath, "a") as outf:
        first = True
        outf.write("INSERT INTO " + table + " VALUES")
        #outf.writelines("\n" + toSQLStr(line) for line in lines)
        for line in lines:
            if first:
                first = False
            else:
                outf.write(",")
            outf.write("\n" + toSQLStr(line))
        outf.write(";")

def writeGOQuery(table, lines, filepath, condition):
    if len(lines) == 0 or not table or not filepath:
        return
    if (VERBOSE):
        print("Generating INSERT query for " + table)
    with open(filepath, "a") as outf:
        for line in lines:
            outf.write("INSERT INTO " + table + " " + toSQLStr(line))
            if isinstance(line, tuple) or isinstance(line, list):
                outf.write("\n" + fill(condition, line))
            else:
                outf.write("\n" + fill(condition, (line)))
            outf.write(";\n")
            

class DataEntry:
    def __init__(self, id):
        self.id = id
        self.ac = []
        self.desc = {"AltName" : {}, 
                     "RecName" : {},
                     "SubName" : {},
                     "Contains" : {
                         "RecName" : {}, 
                         "AltName" : {}, 
                         "SubName" : {}
                     }, 
                     "Includes" : {
                         "RecName" : {}, 
                         "AltName" : {}, 
                         "SubName" : {}
                     }
                    }
        self.flags = []
        self.go = []
        self.keywords = []
        self.gn = {}
        
    # Generates triples from the data. Not updated.
    def triples(self):
        triples = []
        
        # Keywords
        for item in self.keywords:
            triples.append((self.id, "keyword", item))
            
        # Accession numbers
        for item in self.ac:
            triples.append((self.id, "acnumber", item))
            
        # Recommended Names
        if 'RecName' in self.desc:
            for item in self.desc['RecName']:
                triples.append((self.id, "recname", item))
        
        # Alternative Names
        if 'AltName' in self.desc:
            for item in self.desc['AltName']:
                triples.append((self.id, "altname", item))
            
        return triples
    
    # Translates the data to a printable format.
    def __str__(self):
        desc = ""
        desc = desc + "ID=" + self.id 
        desc = desc +"\n\nDescription\n" + str(self.desc)
        desc = desc + "\n\nKeywords\n" + str(self.keywords)
        desc = desc + "\n\nACcessionNumbers\n" + str(self.ac)
        desc = desc + "\n\nGeneNames\n" + str(self.gn)
        desc = desc + "\n\nGeneOntology\n" + str(self.go)
        return desc


# ../Datasets/UniProtKB/unitprot-cancer/unitprot-cancer.txt
def loadFileData(filepath):
    
    cancer_lines = []
       
    splite = filepath.split('.')

    cf = extract(filepath) if splite and splite[-1] == 'gz' else open(filepath)

    if (VERBOSE):
        print("Loading " + filepath)
    
    for line in cf:
        content = split(line, ' ')
        if len(content) > 0 and content[0] in ['ID', 'AC', 'DE', 'GN', 'KW', 'DR']:
            cancer_lines.append((content[0], (' '.join(content[1:]))[:-1]))
            
    if "close" in dir(cf):
        cf.close()
        
    cancerData = []

    # Loop external data

    # The current data entry
    currentEntry = None

    # Those two corresponds to the keys that have been declared 
    # previously in the DataEntry class desc field, category
    # being at the first level and subCategory the second level.

    # Expected values : [Contains, Includes, None]
    subCategory = None

    # Expected values : [AltName, RecName, SubName]
    category = None
                
    for line in cancer_lines:
        
        # If the line is empty, continue on to the next iteration
        if not line[1]:
            continue
        
        # If we encounter an ID line
        if (line[0] == 'ID'):
            # We create a new data entry and store it.
            # All following lines will store their data into this entry, until we meet a new ID line.
            currentEntry = DataEntry(split(line[1].split(' ')[0] , '_')[0])
            cancerData.append(currentEntry)

        elif (line[0] == 'AC'):
            if currentEntry:
                    [currentEntry.ac.append(item.strip()) for item in split(line[1], ';')]
                    
        elif (line[0] == 'KW'):
            if currentEntry:
                    [currentEntry.keywords.append(item.strip()) for item in split(line[1], ';')]
                    
        elif (line[0] == 'DR'):
            if currentEntry:
                        # [:-1] to remove the dot at the end that we don't need
                    semicolonsplit = split(line[1][:-1], ';')
                    # check if the line begins with 'GO', in which case we retrieve the GO number in the line
                    if len(semicolonsplit) > 1 and semicolonsplit[0] == 'GO':
                        goEntry = {}
                        
                        for i in range(1, len(semicolonsplit)):
                            colonsplit2 = split(semicolonsplit[i], ':')
                            goEntry[colonsplit2[0].strip()] = colonsplit2[1].strip()
                            
                        currentEntry.go.append(goEntry)
        
        elif (line[0] == 'GN'):
            
            if currentEntry:
                
                # we ignore the lines that only contains 'and'
                if line[1] == 'and':
                    continue
                    
                # Gene names are separated by semicolons.
                # An item is of the form <category>=<value>[, <value2>, ...].
                for item in split(line[1], ';'):
                    
                    content = split(item, '=')
                    
                    if len(content) > 1:
                        # there may be several values, separated by commas
                        commasplit = split(content[1], ',')
                        for item in commasplit:
                            value = split(item, '{')[0].strip()
                            # we store the value in the array of category
                            appendToSubArray(currentEntry.gn, content[0].strip(), value)
                        
        elif (line[0] == 'DE'):
            if currentEntry:
                colonsplit = split(line[1], ':')
                if len(colonsplit) and colonsplit[0] in ['Contains', 'Includes']:
                    category = colonsplit[0]
                elif len(colonsplit) and colonsplit[0] in ['AltName', 'RecName', 'SubName']:
                    subCategory = colonsplit[0]
                    content = split(colonsplit[1][:-1], '=')
                    
                    # to remove the content between brackets
                    value = split(content[1], '{')[0].strip()
                    if category:
                        appendToSubArray(currentEntry.desc[category][subCategory], content[0].strip(), value)
                    else:
                        appendToSubArray(currentEntry.desc[subCategory], content[0].strip(), value)
                elif colonsplit[0] == 'Flags':
                    currentEntry.flags.append(colonsplit[1][:-1].strip())
                else:
                    content = split(line[1], '=')
                    if len(content) < 2:
                        continue
                    # to remove the content between brackets
                    value = split(content[1][:-1], '{')[0].strip()
                    if category and subCategory:
                        appendToSubArray(currentEntry.desc[category][subCategory], content[0].strip(), value)
                    elif subCategory:
                        appendToSubArray(currentEntry.desc[subCategory], content[0].strip(), value)
    
    return cancerData                

def generateInsertQueries(data, path, uniqueFile=False):
    
    # change your table names here
    id_table = "unitprot"
    ac_table = "accession_number"
    name_table = "description"
    keyword_table = "keyword"
    genename_table = "gene_name"
    gene_ontology_table = "go_unitprot"
    go_table = "go"

    lines = {
        id_table : [],
        ac_table : [], 
        # if you want to have both altname and recname in the same table, use this one
        name_table: [],
        keyword_table : [], 
        genename_table : [], 
        gene_ontology_table : [],
        'go_evidence' : [],
        'go_term' : []}

    go_ids = []

    for entry in data:
        
        # id table
        lines[id_table].append((entry.id, entry.flags[0] if entry.flags else 'NOT AVAILABLE'))
        
        # ac table
        [lines[ac_table].append((entry.id, item)) for item in entry.ac]
        
        # Name table
        # alternative names
        [lines[name_table].append((entry.id, "AltName", k, item)) for k, names in entry.desc["AltName"].items() for item in names]
        [lines[name_table].append((entry.id, "AltName", k, item)) for k, names in entry.desc["Contains"]["AltName"].items() for item in names]
        [lines[name_table].append((entry.id, "AltName", k, item)) for k, names in entry.desc["Includes"]["AltName"].items() for item in names]
        
        # recommended names
        [lines[name_table].append((entry.id, "RecName", k, item)) for k, names in entry.desc["RecName"].items() for item in names]
        [lines[name_table].append((entry.id, "RecName", k, item)) for k, names in entry.desc["Contains"]["RecName"].items() for item in names]
        [lines[name_table].append((entry.id, "RecName", k, item)) for k, names in entry.desc["Includes"]["RecName"].items() for item in names]
        
        # flag table
        #[lines[flag_table].append((entry.id, item)) for item in entry.flags]
        
        # keyword table
        [lines[keyword_table].append((entry.id, item)) for item in entry.keywords]
        
        # gene ontology table
        [lines[gene_ontology_table].append((entry.id, item["GO"])) for item in entry.go]
        
        # gene name table
        [lines[genename_table].append((entry.id, k if "s" not in k else k[:-1], item)) for k, v in entry.gn.items() for item in v]
        
        # Writing GO special queries:
        for hgo in entry.go:
            elems = [i for i in hgo if len(i) == 3]
            if elems:
                lines['go_evidence'].append((hgo['GO'], elems[0], 'NOT AVAILABLE', hgo[elems[0]]))
        
        [lines['go_term'].append((go['GO'], [go[i] for i in go if i in ['F', 'C', 'P']][0])) for go in entry.go]
        
        [go_ids.append(i) for i in [go['GO'] for go in entry.go]]
        
    for key, value in lines.items():
        writeInsertQuery(key, value, path if uniqueFile else dirpath + '/' + str(key) + ".sql")

    # special go query
    writeGOQuery(go_table, go_ids, path if uniqueFile else dirpath + '/' + str(key) + ".sql", 'WHERE NOT (SELECT TRUE FROM go WHERE go_id = $1 LIMIT 1)')
    
# filepath : the file to load
# path : the path (name of single file or directory to store the several files)
# uniqueFile : indicates if we need to create a single file or multiple
def processUnitProtData(filepath, path='.', uniqueFile=True):
    if uniqueFile:
        truepath = '/'.join(path.split('/')[:-1])
        if truepath and not os.path.exists(truepath):
            os.makedirs(truepath)
            print("creating path " + truepath)
    else:
        if not os.path.exists(path):
            os.makedirs(path)
            print("creating path " + path)

    data = loadFileData(filepath)
    generateInsertQueries(data, path, uniqueFile)
 
# in command line : 
# -v to set verbose
# -s to write in a single file (in multiple files otherwise)
# python x <file to load> <path to store the queries>
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Invalid arguments.")
        exit()
    VERBOSE = "-v" in sys.argv
    processUnitProtData(sys.argv[1], sys.argv[2], "-s" in sys.argv)
