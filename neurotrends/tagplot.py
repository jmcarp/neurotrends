# Imports
import os
import re
import operator
import functools
from numpy import linspace

# Project imports
from trendpath import *
from trenddb import *
from pattern import tags as srclist
from util import *
from neurotrends import trendpath

# Import RPy2 modules
import rpy2.robjects as ro
#import rpy2.robjects.lib.ggplot2 as ggplot2
from rpy2.robjects.packages import importr
ggplot2 = importr('ggplot2')

# Import map tools
#filedir = os.path.split(__file__)[0]

print 'source("%s/maplib/maptools.R")' % (trendpath.home_dir)
ro.r('source("%s/maplib/maptools.R")' % (trendpath.home_dir))
#ro.r('source("%s/maplib/maptools.R")' % (filedir))

minartct = 100

def getyears():

    # Get years
    years = [int(year[0]) for year in session.query(Article.pubyear)]

    # Get year range
    ymin = min(years)
    ymax = max(years)
    
    # Get article counts
    for year in range(ymin, ymax + 1):
        artct = session.query(Article)\
            .filter(Article.pubyear == year)\
            .count()
        if artct >= minartct:
            ymin = year
            break

    # Return years
    return range(ymin, ymax + 1)

qyear = range(1998, 2013)
if __name__ == '__main__' and 'qyear' not in locals():
    qyear = getyears()

def getcols(ncols):
    """
    Get ggplot-style colors
    Arguments:
        ncols (int): Number of colors
    """
    
    hues = linspace(15, 375, ncols + 1)
    cols = ro.r.hcl(h=list(hues), l=65, c=100)
    return cols[:-1]

def getsuptags(supname, tagname='none'):
    """
    Get list of super-ordinate tags
    """
    
    fieldname = supname + 'name'
    fieldq = session.query(Field.value).filter(Field.name == fieldname)
    if tagname != 'none':
        fieldq = fieldq.filter(tagname)
    fields = fieldq.all()
    suptags = [field[0] for field in fields]
    return suptags

def attribs2articles(attribs, uniq=False, place=False):
    """
    Get articles tagged with specified attributes
    Arguments:
        attribs (list): Attrib objects
        uniq (bool): Remove duplicate articles?
        place (bool): Restrict to articles with place?
    """

    # Get articles for each attrib
    artgroups = [attrib.articles for attrib in attribs]

    # Return empty list if not artgroups
    if not artgroups:
        return []

    # Flatten article list
    arts = functools.reduce(operator.add, artgroups, [])

    # Get unique articles
    if uniq:
        arts = list(set(arts))
    
    # Require place
    if place:
        arts = [art for art in arts if art.place]

    # Return articles
    return arts

def gettags(supname, tagname='none', tagver='none', tagval='none',
        rettype='query', uniq=True, place=False):
    
    qlist = []
    # 
    clauses = [Field.name == supname + 'name']
    if tagname != 'none':
        if type(tagname) in [str, unicode]:
            valtest = Field.value == tagname
        else:
            valtest = tagname
        clauses.append(valtest)
    q = Attrib.fields.any(and_(*clauses))
    qlist.append(q)

    # Build version query
    if tagver != 'none':
        if type(tagver) in [str, unicode]:
            vertest = Field.value == tagver
        else:
            vertest = tagver
        qver = Attrib.fields.any(
            and_(
                Field.name == supname + 'ver',
                vertest
            )
        )
        q = and_(q, qver)
        qlist.append(qver)

    # Build value query
    if tagval != 'none':
        if type(tagval) in [str, unicode]:
            valtest = Field.value == tagval
        else:
            valtest = tagval
        qval = Attrib.fields.any(
            and_(
                Field.name == supname + 'value',
                valtest
            )
        )
        q = and_(q, qval)
        qlist.append(qval)
    
    if rettype == 'attrib':
        query = session.query(Attrib).filter(q)
        return query.all()
    if rettype == 'articlex':
        query = session.query(Article).filter(Article.attribs.any(qlist[0]))
        for qitem in qlist[1:]:
            query = query.intersect(session.query(Article).filter(Article.attribs.any(qitem)))
        return query.all()
    if rettype == 'articley':
        #query = session.query(Article).filter(Article.attribs.any(q))
        #query = session.query(Article).filter(Article.attribs.any(q)).intersect(session.query(Article).filter(Article.place != None))
        query = session.query(Article).filter(Article.place != None).filter(Article.attribs.any(q))
        #query = session.query(Article).filter(Article.attribs.any(q)).filter(Article.place != None)
        return query.all()
    if rettype == 'article':
        attribs = session.query(Attrib).filter(q).all()
        return attribs2articles(attribs, uniq=uniq, place=place)
        artgroups = [attrib.articles for attrib in attribs]
        artflat = functools.reduce(operator.add, artgroups, [])
        if uniq:
            artflat = list(set(artflat))
        if place:
            artflat = [art for art in artflat if art.place]
        return artflat

    # Run query
    query = session.query(Attrib)
    query = query.filter(q)
    
    # Return results
    if rettype == 'query':
        return query
    elif rettype == 'attrib':
        return query.all()
    elif rettype == 'article':
        artgroups = [attrib.articles for attrib in query.all()]
        artflat = functools.reduce(operator.add, artgroups, [])
        if uniq:
            artflat = list(set(artflat))
        return artflat

def mergevers(verct, verprop, vercoord, verrule=None, vermap=None):
    
    # Build vermap from rule
    if verrule:
        vermap = {}
        for ver in verct:
            newver = verrule(ver)
            vermap[ver] = newver
    
    # Keep missing versions unchanged
    for ver in verct:
        if ver not in vermap:
            vermap[ver] = ver
    
    # Quit if vermap missing
    if not vermap:
        return
    
    fromvers = vermap.keys()
    tovers = list(set(vermap.values()))
    bins = sorted(verct[fromvers[0]].keys())
    
    # Initialize merged versions
    mverct = {}
    mverprop = {}
    mvercoord = {}
    for ver in tovers:
        mverct[ver] = dict([(bin, 0) for bin in bins])
        mverprop[ver] = dict([(bin, 0) for bin in bins])
        mvercoord[ver] = dict([(bin, []) for bin in bins])

    for ver in fromvers:
        tover = vermap[ver]
        for bin in bins:
            mverct[tover][bin] += verct[ver][bin]
            if ver != 'all':
                mverprop[tover][bin] += verprop[ver][bin]
            mvercoord[tover][bin].extend(vercoord[ver][bin])

    return mverct, mverprop, mvercoord

def trimvers(verct, verprop, vercoord, minprop):
    
    trimct = { 'other' : {} }
    trimprop = { 'other' : {} }
    trimcoord = { 'other' : {} }
    bins = qyear + ['all']
    for bin in bins:
        trimct['other'][str(bin)] = 0
        trimprop['other'][str(bin)] = 0
        trimcoord['other'][str(bin)] = []

    for ver in verprop:
        if verprop[ver]['all'] >= minprop:
            trimct[ver] = verct[ver]
            trimprop[ver] = verprop[ver]
            trimcoord[ver] = vercoord[ver]
        else:
            for bin in verprop[ver]:
                trimct['other'][bin] += verct[ver][bin]
                trimprop['other'][bin] += verprop[ver][bin]
                trimcoord['other'][bin].extend(vercoord[ver][bin])
            trimcoord['other']['all'].extend(vercoord[ver]['all'])

    return trimct, trimprop, trimcoord

def vers2frame(vers, incvers=None, bintype='year'):
    'Create data.frame' 
    
    if not incvers:
        incvers = vers.keys()

    # Exclude all version
    trimvers = dict([(v, vers[v]) for v in incvers if v != 'all'])

    vernames = trimvers.keys()
    bins = sorted(trimvers[vernames[0]].keys())
    if bintype == 'year':
        bins = [bin for bin in bins if bin != 'all']
    elif bintype == 'all':
        bins = ['all']

    # 
    bincol = bins * len(trimvers)
    if bintype == 'year':
        rbincol = ro.IntVector(bincol)
    elif bintype == 'all':
        rbincol = ro.FactorVector(bincol)

    # 
    countcol = []
    vercol = []
    for ver in trimvers:
        countcol.extend([vers[ver][bin] for bin in bins])
        vercol.extend([ver] * len(bins))
    
    verSV = ro.StrVector(vercol)
    revvers = incvers
    if bintype == 'year':
        revvers.reverse()
    verlev = ro.StrVector(revvers)

    df = ro.DataFrame({
        'bin' : rbincol,
        'count' : ro.FloatVector(countcol),
        'ver' : ro.FactorVector(verSV, levels=verlev),
    })

    return df

def plotvals(supname, tagname='none', plottype='tag', tagver='none', 
        anytag=False, uniq=True, normbyart=False, exc=[]):
    
    # Normalize by published articles for <any> plots
    if anytag:
        normbyart=True

    # Get tags
    if plottype == 'tag':
        if type(tagname) != list:
            tags = getsuptags(supname, tagname)
        else:
            tags = tagname
    else:
        tags = gettags(supname, tagname=tagname, tagver=tagver, rettype='attrib')
    
    if plottype == 'tag':
        # Get tags
        fieldstr = supname + 'name'
    elif plottype == 'ver':
        # Get versions
        fieldstr = supname + 'ver'
    elif plottype == 'val':
        # Get values
        fieldstr = supname + 'value'

    # Initialize
    artct = {}
    artprop = {}
    artcoord = {}
    
    tagarts = {}
    
    attribs = []
    for tag in tags:
        if plottype == 'tag':
            if anytag:
                attribs.extend(gettags(supname, tag, 
                    rettype='attrib', uniq=uniq))
            else:
                tagarts[tag] = gettags(supname, tag, 
                    rettype='article', uniq=uniq)
        elif plottype == 'ver':
            tagval = tag.fields[fieldstr].value
            if anytag:
                attribs.extend(gettags(supname, tagname, tagver=tagval, 
                    rettype='attrib', uniq=uniq))
            else:
                tagarts[tagval] = gettags(supname, tagname, tagver=tagval, 
                    rettype='article', uniq=uniq)
        elif plottype == 'val':
            tagval = tag.fields[fieldstr].value
            if anytag:
                attribs.extend(gettags(supname, tagname, tagval=tagval, 
                    rettype='attrib', uniq=uniq))
            else:
                tagarts[tagval] = gettags(supname, tagname, tagval=tagval, 
                    rettype='article', uniq=uniq) 

    if anytag:
        tagarts['any'] = attribs2articles(attribs, uniq=True)

    for tag in tagarts:
        artct[tag] = {
            'all' : len(tagarts[tag]),
        }
        artcoord[tag] = {
            'all' : [(art.place.lon, art.place.lat) for art in tagarts[tag] if art.place]
        }
        for year in qyear:
            syear = str(year)
            yarts = [art for art in tagarts[tag] if art.pubyear == syear]
            artct[tag][syear] = len(yarts)
            artcoord[tag][syear] = [(art.place.lon, art.place.lat) for art in yarts if art.place]
    
    artct['all'] = {}
    if normbyart:
        artct['all']['all'] = session.query(Article)\
            .filter(or_(Article.htmlfile != None, Article.pdftxtfile != None))\
            .count()
    else:
        artct['all']['all'] = sum([artct[tag]['all'] for tag in tagarts])
    artcoord['all'] = {}
    artcoord['all']['all'] = functools.reduce(
        operator.add, [artcoord[tag]['all'] for tag in tagarts], [])
    for year in qyear:
        syear = str(year)
        if normbyart:
            artct['all'][syear] = session.query(Article)\
            .filter(Article.pubyear == syear)\
            .filter(or_(Article.htmlfile != None, Article.pdftxtfile != None))\
            .count()
        else:
            artct['all'][syear] = sum([artct[tag][syear] for tag in tagarts])
        artcoord['all'][syear] = functools.reduce(
            operator.add, [artcoord[tag][syear] for tag in tagarts], [])

    for tag in tagarts:
        artprop[tag] = {
            'all' : artct[tag]['all'] / float(artct['all']['all']),
        }
        for year in qyear:
            syear = str(year)
            if artct['all'][syear]:
                prop = float(artct[tag][syear]) / artct['all'][syear]
            else:
                prop = 0
            artprop[tag][syear] = prop
    
    return artct, artprop, artcoord

def plotmap(location, zoom, title, supname, tagname='none', plottype='tag', 
        verrules=[], vermap={}, vars=None, dv='count', uniq=False, 
        minprop=None, sort=None, custcols=False, k=3, fmt='png', outname=None):
     
    # Get versions
    verct, verprop, vercoord = plotvals(supname, tagname, plottype=plottype, uniq=uniq)
    
    # Merge versions
    if verrules:
        for verrule in verrules:
            verct, verprop, vercoord = mergevers(verct, verprop, vercoord, verrule=verrule)
    if vermap:
        verct, verprop, vercoord = mergevers(verct, verprop, vercoord, vermap=vermap)
    
    # Trim minority versions
    if minprop:
        verct, verprop, vercoord = trimvers(verct, verprop, vercoord, minprop=minprop)
    
    # Build data frame
    lon = []
    lat = []
    pkg = []
    pyr = []

    for tag in vercoord:
        if tag == 'all':
            continue
        for year in qyear:
            syear = str(year)
            lon.extend([coord[0] for coord in vercoord[tag][syear]])
            lat.extend([coord[1] for coord in vercoord[tag][syear]])
            pkg.extend([tag] * len(vercoord[tag][syear]))
            pyr.extend([year] * len(vercoord[tag][syear]))
    
    df = ro.DataFrame({
        'lon' : ro.FloatVector(lon),
        'lat' : ro.FloatVector(lat),
        'pkg' : ro.StrVector(pkg),
        'pyr' : ro.StrVector(pyr),
    })
    
    # Get map
    rmap = ro.r.get_map(location=location, zoom=zoom)
    gmap = ro.r.ggmap(rmap)

    # Make pie chart map
    # Note: Call function using robjects dict to avoid dot conflict
    outname = '%s/map/%s-year' % (figdir, outname)
    ro.r['plot.groups'](df, gmap, k=k, maxsize=0.09, 
        splitvar='pyr', title=title, outname=outname)
    ro.r['plot.groups'](df, gmap, k=k, maxsize=0.09, 
        title=title, outname=outname)

def makeverplot(supname, tagname, plottype='tag', anytag=False, 
        verrules=None, vermap={}, vars=None, dv='count', uniq=False, 
        normbyart=False, minprop=None, sort='count', bintype='year',
        custcols=False, title='', fmt='png', outname=None):
    
    # Get versions
    verct, verprop, vercoord = plotvals(supname, tagname, plottype=plottype, anytag=anytag, uniq=uniq, normbyart=normbyart)
    
    # Merge versions
    if verrules and not anytag:
        for verrule in verrules:
            verct, verprop, vercoord = mergevers(verct, verprop, vercoord, verrule=verrule)
    if vermap and not anytag:
        verct, verprop, vercoord = mergevers(verct, verprop, vercoord, vermap=vermap)
    
    # Trim minority versions
    if minprop and not anytag:
        verct, verprop, vercoord = trimvers(verct, verprop, vercoord, minprop=minprop)
    
    if not vars:
        vars = verct.keys()

    # Sort labels
    if sort:

        # Get sort method
        if sort == 'alpha':
            key = None
            reverse = False
        elif sort == 'count':
            key = lambda k: verct[k]['all']
            reverse = True
        
        # Sort variables
        vars = sorted(vars, key=key, reverse=reverse)

    # Move <other> and <none> to end
    ordvars = [var for var in vars if var not in ['all', 'other', 'none']]

    # Get custom colors
    if custcols:
        cols = getcols(len(ordvars))
    
    # Add <other> label
    if 'other' in verct and verct['other']['all']:
        ordvars.append('other')
        if custcols:
            cols = ro.r.c('#ABABAB', cols)
            #cols = ro.r.c('gray', cols)

    # Add <none> label
    if 'none' in verct and verct['none']['all']:
        ordvars.append('none')
        if custcols:
            cols = ro.r.c('#808080', cols)
            #cols = ro.r.c('gray', cols)

    # Reverse custom colors for <all> bin
    if bintype == 'all' and 'cols' in locals():
        cols = ro.r.rev(cols)
            
    # Get variables
    if anytag:
        vars = ['any']
    else:
        vars = ordvars

    # Get data.frame
    if dv == 'count':
        verdf = vers2frame(verct, vars, bintype=bintype)
    elif dv == 'prop':
        verdf = vers2frame(verprop, vars, bintype=bintype)
    
    labargs = {}

    # Get y-label
    if dv == 'count':
        labargs['y'] = 'Count'
    elif dv == 'prop':
        labargs['y'] = 'Proportion'

    # Set up aes() arguments
    aesargs = {}
    aesargs['y'] = 'count'
    if bintype == 'year':
        aesargs['x'] = 'bin'
    elif bintype == 'all':
        aesargs['x'] = 'ver'
    if len(vars) > 1:
        aesargs['fill'] = 'ver'
        aesargs['order'] = '-as.numeric(ver)'
    
    # Append ": Any" to title for anytag
    if anytag:
        title += ': Any'

    # Build plot
    gp = ggplot2.ggplot(verdf) + \
        ggplot2.aes(**aesargs) + \
        ggplot2.geom_bar(stat='identity', position='stack') + \
        ro.r.labs(**labargs) + \
        ggplot2.opts(title=title)

    # Hide legend for bintype <all>
    if bintype == 'all':
        gp += ro.r('opts(legend.position="none")')
    else:
        gp += ro.r.guides(fill=ro.r.guide_legend(title=ro.NULL))
 
    # Rotate x-labels for bintype <all>
    if bintype == 'year':
        xangle = 0
    elif bintype == 'all':
        xangle = 45

    # Set font sizes
    gp += ro.r('opts(plot.title=theme_text(size=24))')
    gp += ro.r('opts(axis.title.x=theme_text(size=18))')
    gp += ro.r('opts(axis.text.x=theme_text(size=14, angle=%d))' % (xangle))
    gp += ro.r('opts(axis.title.y=theme_text(size=18, angle=90, vjust=0.33))')
    gp += ro.r('opts(axis.text.y=theme_text(size=14, angle=90))')

    # Hide x-label
    gp += ro.r('opts(axis.title.x=theme_blank())')

    # Add loess trend for one-variable plots
    if len(vars) == 1:
        gp += ggplot2.stat_smooth(method='loess', formula='y~x', se=False, size=3)

    # Add colors
    if custcols and not anytag:
        gp += \
            ggplot2.scale_fill_manual(values=cols)
    
    # Show plot    
    gp.plot()
    
    # Save plot
    if outname:
        # Change output extention to <fmt>
        outroot, outext = os.path.splitext(outname)
        outname = '%s.%s' % (outroot, fmt)
        # Include default dimensions to suppress ggsave output
        ro.r.ggsave(outname, height=7, width=7)

def plotonetag(supname, tagname):
    
    makeverplot(supname, [tagname], plottype='tag', 
        vars=[tagname], dv='prop', bintype='year', normbyart=True,
        title=tagname,
        outname='%s/one/%s-%s' % (figdir, supname, tagname))

def plotspmvers(name='', dv='count', bintype='year', anytag=False):
    
    verrules = [
        lambda v: re.sub('(?<=\d)[a-zA-Z]+', '', v),
    ]
    vermap = {
        '' : 'none',
    }
    vernames = ['none', '96', '97', '99', '2', '5', '8']
    makeverplot('pkg', 'spm', plottype='ver', uniq=False, 
        verrules=verrules, vermap=vermap, custcols=True, dv=dv, sort=None,
        vars=vernames, title='SPM Version', bintype=bintype, anytag=anytag,
        outname='%s/grp/spmver-%s' % (figdir, name))

def matver(ver):
    
    if ver == 'all':
        return 'all'
    return ver[:1]

def plotmatvers(name='', dv='count', bintype='year', anytag=False):
    
    verrules = [
        matver,
    ]
    vermap = {
        '' : 'none',
    }
    makeverplot('lang', 'matlab', plottype='ver', uniq=False,
        custcols=True, dv=dv, verrules=verrules, vermap=vermap,
        sort='alpha', minprop=0.01,
        title='Matlab Version', bintype=bintype, anytag=anytag,
        outname='%s/grp/matver-%s' % (figdir, name))

def plotfield(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('mag', 'field', plottype='val', anytag=anytag, 
        uniq=False, dv=dv, bintype=bintype,
        minprop=0.01, sort='alpha', custcols=True, title='Field Strength',
        outname='%s/grp/field-%s' % (figdir, name))

def plotpkgs(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('pkg', 'none', plottype='tag', anytag=anytag,
        minprop=0.01, dv=dv, custcols=True, title='Software Package',
        bintype=bintype,
        outname='%s/grp/pkg-%s' % (figdir, name))

def plottask(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('task', 'none', plottype='tag', anytag=anytag,
        minprop=0.01, dv=dv, custcols=True, title='Task Presentation Package',
        bintype=bintype,
        outname='%s/grp/task-%s' % (figdir, name))

def plotdes(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('des', 'none', plottype='tag', anytag=anytag,
        dv=dv, custcols=True, title='Design', bintype=bintype,
        outname='%s/grp/des-%s' % (figdir, name))

def plotaccel(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('pulse', Field.value.in_(['sense', 'grappa', 'presto', 'smash']), plottype='tag', anytag=anytag,
    dv=dv, bintype=bintype, custcols=True, title='Acceleration Method',
    outname='%s/grp/accel-%s' % (figdir, name))

def plotseq(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('pulse', Field.value.in_(['gradient', 'spin', 'grase']), plottype='tag', anytag=anytag,
    dv=dv, bintype=bintype, custcols=True, title='Acquisition Sequence',
    outname='%s/grp/seq-%s' % (figdir, name))

def plottraj(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('pulse', Field.value.in_(['epi', 'spiral']), plottype='tag', anytag=anytag,
    dv=dv, bintype=bintype, custcols=True, title='Acquisition Trajectory',
    outname='%s/grp/traj-%s' % (figdir, name))

def plotlang(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('lang', 'none', plottype='tag', anytag=anytag,
        dv=dv, bintype=bintype, custcols=True, title='Programming Language',
        minprop=0.005,
        outname='%s/grp/lang-%s' % (figdir, name))

def plotmod(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('mod', tagname=~Field.value.in_(['rfx', 'ffx']), 
        plottype='tag', anytag=anytag, dv=dv, bintype=bintype,
        custcols=True, title='Model',
        outname='%s/grp/mod-%s' % (figdir, name))

def plotmcc(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('mcc', 'none', plottype='tag', anytag=anytag,
        dv=dv, bintype=bintype, custcols=True, title='Multiple Comparison Correction',
        outname='%s/grp/mcc-%s' % (figdir, name))

def plotopsys(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('opsys', tagname=~Field.value.in_(['solaris']),
        plottype='tag', anytag=anytag,
        dv=dv, bintype=bintype, custcols=True, title='Operating System',
        outname='%s/grp/os-%s' % (figdir, name))

def plotmagvend(name='', dv='count', bintype='year', anytag=False):
    
    makeverplot('mag', tagname=~Field.value.in_(['field', 'varian']),
        plottype='tag', anytag=anytag, dv=dv, bintype=bintype,
        outname='%s/grp/magvend-%s' % (figdir, name),
        title='Magnet Vendor')

def plotpkgmap(location='london, uk', zoom=8, locshort=''):
    
    # Get short location
    if not locshort:
        locshort = location.split(',')[0]

    # Get output name
    outname = 'pkg-%s' % (locshort)

    # Plot
    plotmap(location, zoom, 'Package', 'pkg', plottype='tag', 
        minprop=0.05, outname=outname)

def argh():
    
    plotpkgmap(location='london, uk', zoom=8)
    plotpkgmap(location='boston, ma', zoom=8)
    plotpkgmap(location='california', zoom=6)

plottypes = [
    {'name' : 'count-all', 'dv' : 'count', 'bintype' : 'all'},
    {'name' : 'count-year', 'dv' : 'count', 'bintype' : 'year'},
    {'name' : 'prop-year', 'dv' : 'prop', 'bintype' : 'year'},
    {'name' : 'prop-any', 'dv' : 'prop', 'bintype' : 'year', 'anytag' : True},
]

def batchplottime():
    
    for plottype in plottypes:
        plotpkgs(**plottype)
        plotmagvend(**plottype)
        plotmod(**plottype)
        plotmcc(**plottype)
        plotdes(**plottype)
        plotfield(**plottype)
        plotspmvers(**plottype)
        plotmatvers(**plottype)
        plottask(**plottype)
        plotlang(**plottype)
        plotaccel(**plottype)
        plottraj(**plottype)
        plotseq(**plottype)
        plotopsys(**plottype)

def batchplotone():
    
    for srcgrp in srclist:
        for tag in srclist[srcgrp]['src']:
            plotonetag(srcgrp, tag)
