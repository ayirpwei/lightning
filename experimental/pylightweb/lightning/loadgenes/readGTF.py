import csv
import sys
import string

def printProgress(i, total):
    foo = 100 * i/float(total)
    sys.stdout.write("\r%f%%" %foo)
    sys.stdout.flush()
    
def getStartTile(chrom, chr_start, loci):
    for i, thing in enumerate(loci[chrom]):
        start, end, tile = thing
        if start <= chr_start and end > chr_start:
            return tile
        elif start > chr_start:
            print chrom, start, end, chr_start
            print loci[chrom][i-1]
            print "getStartTile, Reached the end of loci without returning tile"
            return None

def getEndTile(chrom, chr_end, loci):
    for start, end, tile in loci[chrom]:
        if end >= chr_end and start < chr_end:
            return tile
        elif start > chr_end:
            print chrom, start, end, chr_end
            print "getEndTile Reached the end of loci without returning tile"
            return None

def manipulateList(inpList):
    retlist = []
    for l in inpList:
        thingsToJoin = []
        for foo in l:
            thingsToJoin.append(str(foo))
        thingsToJoin[-1] += '\n'
        retlist.append(string.join(thingsToJoin, sep=','))
    return retlist

known_genes_file = 'hide/GeneReview/NBKid_shortname_genesymbol.txt'
genes = {}
with open(known_genes_file, 'r') as f:
    for line in f:
        if line[0] != '#':
            NBKid, shortname, geneName = line.split('\t')
            geneName = geneName.split('\n')[0]
            if geneName != 'Not applicable':
                if geneName in genes:
                    genes[geneName] += ';http://www.ncbi.nlm.nih.gov/books/' + NBKid
                else:
                    genes[geneName] = 'http://www.ncbi.nlm.nih.gov/books/' + NBKid


supported_chr = {str(i+1):i+1 for i in range(22)}
supported_chr['X'] = 23
supported_chr['Y'] = 24
supported_chr['MT'] = 25

loci = [[] for i in range(26)]

with open('hide/varlocusannotation.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for line in reader:
        tilename = hex(int(line[0]))[2:].zfill(12)
        tilename = int(tilename[:-3], 16)
        chrom = int(line[2]) - 1
        chr_start = int(line[3])
        chr_end = int(line[4])
        loci[chrom].append((chr_start, chr_end, tilename))

for i, chromosome in enumerate(loci):
    loci[i] = sorted(chromosome, key=lambda i: i[0])
        


poss_sources = set()
fname = 'hide/Homo_sapiens.GRCh37.75.gtf'
num_lines = sum(1 for line in open(fname))
towrite = []
with open(fname, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for prog, line in enumerate(reader):
        if prog % 100 == 0:
            printProgress(prog, num_lines)
        # line organization:
        #   seqname, source, feature, startCGF, endCGF, score, strand, frame
        if line[0][0] != '#':
            #towriteline: seqname, source, feature, startCGF, endCGF, score, strand, frame, ...
            #             gene_id, gene_source, gene_name, gene_biotype, transcript_id, ...
            #             transcript_source, transcript_biotype, transcript_name, exon_id, ...
            #             exon_number, protein_id, genereview, genereviewURLs
            towriteline = []
            #Currently only parsing genes in supported chromosomes.
            #Though the indexing currently supports alternate chromosomes, tiles don't exist for them yet
            #   -> chrom = 25
            if line[0] in supported_chr and line[2] == "gene":
                chrom = supported_chr[line[0]] - 1
                towriteline.append(chrom+1) #append seqname
                towriteline.append(line[1]) #append source
                towriteline.append(line[2]) #append feature
                #Get CGF coordinates for start position
                chr_start = int(line[3])
                CGF_start = getStartTile(chrom, chr_start, loci)
                towriteline.append(CGF_start) #append CGF_start
                #Get CGF coordinates for end position
                chr_end = int(line[4])
                CGF_end = getEndTile(chrom, chr_end, loci)
                towriteline.append(CGF_end) #append CGF_start
                #append strand
                if line[6] == '+':
                    towriteline.append('t')
                elif line[6] == '-':
                    towriteline.append('f')
                else:
                    print 'Strand not specified'
                    towriteline.append('')
                #append score
                if line[5] != '.':
                    towriteline.append(line[5])
                else:
                    towriteline.append('')
                #append frame (if not '.', will be 0, 1, or 2)
                if line[7] != '.':
                    towriteline.append(line[7])
                else:
                    towriteline.append('')
                #Parse the optional attribute line
                attributes = line[8].split(';')
                #Preset the attributes to null ('')
                parsed_attr = ['' for i in range(11)]
                parser = {'gene_id':0, 'gene_source':1, 'gene_name':2, 'gene_biotype':3, 'transcript_id':4,
                          'transcript_source':5, 'transcript_biotype':6, 'transcript_name':7, 'exon_id':8,
                          'exon_number':9, 'protein_id':10}
                for attr in attributes:
                    if len(attr.strip().split(' ')) > 1:
                        attr_key, attribute = attr.strip().split(' ')
                        attribute = attribute.strip('"')
                        if attr_key in parser:
                            parsed_attr[parser[attr_key]] = attribute
                #Append all attributes to line
                
                towriteline.extend(parsed_attr)
                geneName = towriteline[10]
                if geneName in genes:
                    towriteline.extend(['t', genes[geneName]])
                else:
                    towriteline.extend(['f', ''])
                towrite.append(towriteline)

print ""
print len(towrite)
with open('hide/gene.csv', 'w') as f:
    f.writelines(manipulateList(towrite))


