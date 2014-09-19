# all the imports
import os, sys
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy as sqla


try: #we are deploying locally with python
    from databaseconfig import secretkey, username, password
    SECRET_KEY, USERNAME, PASSWORD = secretkey, username, password
    DEBUG = True
except ImportError: #we are running foreman or on heroku
    pass
    #SECRET_KEY = os.environ.get('SECRETKEY') 
    #USERNAME = os.environ.get('USERNAME')
    #PASSWORD = os.environ.get('PASSWORD')
    #DEBUG = False

# create our little application :)

app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config.from_pyfile('databaseconfig.py')
db = sqla(app)

#hardcoded lists of population, genome, chromosome for now
populations = ['Personal Genome Project']
abvfnames = [s[:-4] for s in os.listdir('./abv') if s.endswith('.abv')]
genomes = ['hg19']
chromosomes = ['chr9']

#this is really dumb. there has to be a python library for b64 that does this already
def a2base64index(foochar):
    std_base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    b64 = range(64)
    lookup = dict(zip(std_base64chars,b64))
    index = lookup[foochar]
    return index #maps D to 3, etc.

def findtilevar(genome, path, step):
    fname = './abv/' + genome + '.abv'
    with open(fname, 'r') as f: ##TODO: will break? if fname does not exist. we should raise useful error mesage here.
        tiles = f.read().split(' ')[1:] #[1: get rid of genome name at beginning of ABV
        tiles = dict(zip(tiles[::2], tiles[1::2])) #turn it from '0', 'seq0', '1', 'seq1' to a dictionary with keys 0, 1, ...
        tile = tiles[path]
        var = tile[int(step)]
        return var

def findallele(tile_id, tilevar, coordinate, begin_int):
    if tilevar == '-':
        return 'No call'
    elif tilevar == '#':
        return 'No data available (lost in encoding as ABV file)' 
    elif tilevar == '.':
        tilevarname = int(tile_id + '000', 16)
    #at some point, need to deal with "complex" cases
    else: #okay, so convert to base 64 key, and then subtract 2, then append to the tile_id as 3 digits (pad with zero)
        foo =  a2base64index(tilevar)-2
        tilevarname = tile_id + foo.zfill(3)
        tilevarname = int(tilevarname, 16)
    #cursor = g.db.execute('SELECT * FROM loadgenomes_tilevariant WHERE %s = tile_variant_name', [tilevarname])
    cursor = g.db.execute('SELECT * FROM loadgenomes_tilevariant WHERE %s = tile_variant_name', tilevarname)
    row = cursor.fetchone()
    seq = row['sequence']
    index = coordinate - begin_int + 1
    return seq[index]

def connect_db():
    return db.engine.connect()

@app.before_request
def before_request():
    g.db = connect_db() 

def init_db():
    pass

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()


@app.route('/')
def show_search():
  return render_template('search.html', populations=populations, genomes=genomes, chromosomes=chromosomes)

@app.route('/search', methods=['POST'])
def search_entries():
    ## TODO: check for valid entries e.g. coordinate is an int :)
    search_pop, search_gen, search_chrom, search_coord, search_allele = \
            str(request.form['search_pop']), request.form['search_gen'], request.form['search_chrom'], int(request.form['search_coord']), request.form['search_allele'], 

    cursor = g.db.execute('SELECT * FROM loadgenomes_tilelocusannotation WHERE %s > begin_int AND %s < end_int LIMIT 1', [search_coord, search_coord])
    row = cursor.fetchone()
    tile_id = format(row['tile_id'], 'x') #1c4000002
    begin_int = row['begin_int']

    path = tile_id[:3] #first three digits
    step = tile_id[-2:] #last two digits

    result = None
    count = 0
    foundabvs, foundpaths, foundsteps, foundvars, foundalleles = [],[],[],[],[]
    #debuglists = [foundabvs, foundpaths, foundsteps, foundvars, foundalleles] 
    debugmsg = []
    for abv in abvfnames:
        tilevar = findtilevar(abv, path, step)
        allele = findallele(tile_id, tilevar, search_coord, begin_int)
        debuginfo = [abv, path, step, tilevar, allele]
        debugmsg.append(debuginfo)
        if (allele == search_allele):
            count += 1

    if count != 0:
        result = True 
    else:
        result = False 

    #msg = tile_id, ' ', path, ' ', step, ' ', tilevar, ' ', allele, ' ', result
    if result == None:
        flash('No results found, try again.')
    else:
        flash(result)
    msg = 'You searched for: allele "'+ search_allele + '" at coordinate "' + str(search_coord) + \
            '" (in ' + search_chrom + ', ' + search_gen + ', ' + search_pop + '). \n\n' 
    if DEBUG:
        msg += 'DEBUG: \n'
        debugmsg = "\n".join(map(lambda x: str(x), debugmsg))
        msg += debugmsg

    return render_template('search.html', msg=msg, result=result, populations=populations, genomes=genomes, prev_pop=search_pop, \
            prev_gen=search_gen, chromosomes=chromosomes, prev_chrom = search_chrom, coordinate=search_coord, allele = search_allele)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
