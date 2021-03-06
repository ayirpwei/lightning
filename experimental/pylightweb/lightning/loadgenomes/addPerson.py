#Add person
import json
import datetime
import string

def addAnnotations(annotations, tile_variant_id, today):
    """
    annotations: list of annotations read in from FASTJ format
    tile_variant_id: the primary key for the tile_variant to add the annotations to
    today: the date

    Requires Phase to be in annotation: determines whether reference or human!

    if SNP, SUB, or INDEL in an annotation, it is marked as SNP_INDEL
    if db_xref in an annotation, it is marked as DATABASE
    if none of the above, and 'alleles' is not in the annotation, it is marked as OTHER (only for debugging purposes)

    no phenotypic data is known to be passed from the FASTJ file
    """
    # for loadgenomes_tilevarannotation: tile_variant_id, annotation_type, source, annotation_text, phenotype, created, last_modified
    lists_to_extend = []
    for annotation in annotations:
        add = True
        if annotation.startswith('hu') or ('GAP' in annotation):
            #These are population specific tags and should not be documented in the tile library
            add = False
        elif 'Phase' in annotation:
            #This is another population-sepecific tag
            add = False
            if 'REF' in annotation:
                pop_size_increment = 0
            else:
                pop_size_increment = 1
        elif 'SNP' in annotation or 'SUB' in annotation or 'INDEL' in annotation:
            t='SNP_INDEL'
        elif 'db_xref' in annotation:
            t='DATABASE'
            annotation = annotation.replace(',', ' ')
        elif 'alleles' in annotation:
            #Cannot be a database annotation; is identical to SNP annotation; is unhelpful.
            add=False
        else:
            t='OTHER'
        if add:
            lists_to_extend.append([tile_variant_id, t, 'library_generation', annotation, '', today, today])

    return lists_to_extend, pop_size_increment

def manipulateList(inpList):
    retlist = []
    for l in inpList:
        thingsToJoin = []
        for foo in l:
            if not foo and type(foo) == str:
                thingsToJoin.append('""')
            else:
                thingsToJoin.append(str(foo))
        thingsToJoin[-1] += '\n'
        retlist.append(string.join(thingsToJoin, sep=','))
    return retlist
            
now = datetime.date.today()
today = str(now.year) + "-" + str(now.month) + "-" + str(now.day)

input_file = 'huA05317.fj'
curr_data_file = '2014-09-15-data.csv'

CHR_CHOICES = {
    'chr1': 1,
    'chr2': 2,
    'chr3': 3,
    'chr4': 4,
    'chr5': 5,
    'chr6': 6,
    'chr7': 7,
    'chr8': 8,
    'chr9': 9,
    'chr10': 10,
    'chr11': 11,
    'chr12': 12,
    'chr13': 13,
    'chr14': 14,
    'chr15': 15,
    'chr16': 16,
    'chr17': 17,
    'chr18': 18,
    'chr19': 19,
    'chr20': 20,
    'chr21': 21,
    'chr22': 22,
    'chrX': 23,
    'chrY': 24,
    'chrM': 25,
}
popul_tilevars = {}
curr_tilevars = {}
tilevars_to_write = []
annotations_to_write = []

#\copy loadgenomes_tilevariant(tile_variant_name, tile_id, population_size, md5sum) to '2014-09-15-data.csv'
with open(curr_data_file, 'r') as f:
    for line in f:
        tile_variant_name, tile_id, popul, md5sum = line.strip().split(',')
        tile_id = int(tile_id)
        if tile_id not in popul_tilevars:
            popul_tilevars[tile_id] = [[tile_variant_name, md5sum, int(popul), False]]
        else:
            popul_tilevars[tile_id].append([tile_variant_name, md5sum, int(popul), False])
            

with open(input_file, 'r') as f:   
    i = 0
    j = 0
    for line in f:
        if (line[:2] == '>{' or line[:3] == '> {') and i > 0:
            #Append csv statements
            # NOTE: The population_size is going to be twice the number of humans
            # things to add:
            #   for loadgenomes_tilevariant: tile_variant_name, tile_id, length, population_size, md5sum, last_modified, sequence, start_tag, end_tag
            #       start_tag and end_tag only if they differ from the reference (from tags[tile_id])
            #   for loadgenomes_tilevarannotation: tile_variant_id, annotation_type, source, annotation_text, phenotype, created, last_modified
            # things to modify using tile_variant_name:
            #   for loadgenomes_tilevariant: population_size

            #Modify if tilevariant is present in popul_tilevars
            #Add otherwise
            write_new = True
            tile_hex = toSaveData['tilename']
            tile_int = int(tile_hex, 16)
            #Check if we have the tile_variant in current database
            tilevars_in_database = popul_tilevars[tile_int]
            for index, variant in enumerate(tilevars_in_database):
                if toSaveData['md5sum'] == variant[1]:
                    write_new = False
                    popul_tilevars[tile_int][index][2] += 1 #Add 1 to the population
                    popul_tilevars[tile_int][index][3] = True #Indicate we will need to update the tilevariant
            #Modify current files
            if write_new:
                if tile_hex not in curr_tilevars:
                    curr_tilevars[tile_hex] = [len(tilevars_to_write)]
                else:
                    poss_tile_indices = curr_tilevars[tile_hex]
                    for index in poss_tile_indices:
                        if toSaveData['md5sum'] == tilevars_to_write[index][4]:
                            write_new = False
                            tilevars_to_write[index][3] += 1
                    if write_new:
                        curr_tilevars[tile_hex].append(len(tilevars_to_write))
            if write_new:
                varname = hex(len(popul_tilevars[tile_int]) + len(curr_tilevars[tile_hex]) -1)[2:].zfill(3)
                tilevarname = int(tile_hex+varname, 16)
                annotations, population_incr = addAnnotations(loadedData[u'notes'], tilevarname, today)
                tilevars_to_write.append([tilevarname, tile_int, toSaveData['length'], population_incr, toSaveData['md5sum'], today, toSaveData['sequence'],
                                          toSaveData['start_seq'], toSaveData['end_seq']])
                annotations_to_write.extend(annotations)
        if (line[:2] == '>{' or line[:3] == '> {'):
            j = 0
            i += 1
            toSaveData = {}
            loadedData = json.loads(line[1:])
            
            tilename = str(loadedData[u'tileID'])
            band, path, tile, variant = tilename.split('.')
            tile = tile.zfill(4)
            toSaveData['tilename'] = band+path+tile
            toSaveData['start_tag'] = str(loadedData[u'startTag'])
            toSaveData['end_tag'] = str(loadedData[u'endTag'])
            toSaveData['start_seq'] = ""
            toSaveData['end_seq'] = ""
            #Will only need to add 'start_tag' and 'end_tag' when using non-reference data which has SNPs on tags
            if u'startSeq' in loadedData:
                if str(loadedData[u'startTag']).lower() != str(loadedData[u'startSeq']).lower():
                    toSaveData['start_seq'] = str(loadedData[u'startSeq'])
                if str(loadedData[u'endTag']).lower() != str(loadedData[u'endSeq']).lower():
                    toSaveData['end_seq'] = str(loadedData[u'endSeq'])
            toSaveData['length'] = loadedData[u'n']
            toSaveData['sequence'] = ''
            toSaveData['md5sum'] = str(loadedData[u'md5sum'])

            locus = str(loadedData[u'locus'][0][u'build'])
            locus = locus.split()
            if locus[0] == 'hg19':
                toSaveData['assembly'] = 19
            if locus[1] in CHR_CHOICES:
                toSaveData['chromosome'] = CHR_CHOICES[locus[1]]
                toSaveData['chrom_name'] = ""
            else:
                toSaveData['chromosome'] = 26
                toSaveData['chrom_name'] = locus[1]
            toSaveData['locus_begin'] = max([0, eval(locus[2])])
            toSaveData['locus_end'] = eval(locus[3])
        elif line != '\n':
            j += 1
            if j < 20000:
                toSaveData['sequence'] += line.strip()
            elif j == 20000:
                print "Tile was too long to reasonably store in memory"
                toSaveData['sequence'] += " ERROR: READ IS TOO LONG TO REASONABLY STORE IN MEMORY "


with open('hide/tilevariant.csv', 'w') as f:
    f.writelines(manipulateList(tilevars_to_write))
with open('hide/varannotation.csv', 'w') as f:
    f.writelines(manipulateList(annotations_to_write))

with open('hide/update.sql', 'w') as f:
    f.write("BEGIN;\n")
    for tiles in popul_tilevars:
        for variant in popul_tilevars[tiles]:
            if variant[3]:
                f.write("UPDATE loadgenomes_tilevariant SET population_size = " + str(variant[2]) + " WHERE tile_variant_name = " + variant[0] + ";\n")
    f.write("COMMIT;\n")

with open('hide/Library.csv', 'w') as f:
    #tilevarname, popul, md5sum
    #Need to write out the ones already in the database and the ones we updated
    for tiles in popul_tilevars:
        for variant in popul_tilevars[tiles]:
            tile_variant_name, md5sum, popul, updated = variant
            tile_var_hex = hex(int(tile_variant_name))[2:]
            tile_var_hex = tile_var_hex.zfill(12)
            path = tile_var_hex[:3]
            version = tile_var_hex[3:5]
            step = tile_var_hex[5:9]
            var = tile_var_hex[9:]
            tile_var_period_sep = string.join([path, version, step, var], '.') 
            f.write(string.join([tile_var_period_sep, str(popul), md5sum+'\n'], sep=','))
    for l in tilevars_to_write:
        tile_variant_name, tile_id, length, population_size, md5sum, last_modified, sequence, start_tag, end_tag = l
        tile_var_hex = hex(tile_variant_name)[2:]
        tile_var_hex = tile_var_hex.zfill(12)
        path = tile_var_hex[:3]
        version = tile_var_hex[3:5]
        step = tile_var_hex[5:9]
        var = tile_var_hex[9:]
        tile_var_period_sep = string.join([path, version, step, var], '.') 
        f.write(string.join([tile_var_period_sep, str(population_size), md5sum+'\n'], sep=','))
