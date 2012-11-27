
# 
import re
from scipy.stats import norm

# Import project modules
from tagplot import *

def checkart(art, attribs):
  
  art = toart(art)
  return any([attrib in art.attribs for attrib in attribs])

def getpipe(art, attgrps):

  pipe = {}

  for attgrp in attgrps:
    pipe[attgrp] = checkart(art, attgrps[attgrp])

  return pipe

def varbyyear(attmaps):
  
  result = dict([(attmap, []) for attmap in attmaps])
  pipetot = dict([(attmap, []) for attmap in attmaps])

  orfilt = or_(Article.htmlfile != None, Article.pdftxtfile != None)

  for year in qyear:
    
    print 'Working on year %d...' % (year)

    syear = str(year)
    arts = session.query(Article)\
      .filter(Article.pubyear == syear)\
      .filter(orfilt)\
      .all()
    
    for attmap in attmaps:

      pipeyear = []

      for art in arts:
        pipeyear.append(getpipe(art, attmaps[attmap]))

      pipetot[attmap].extend(pipeyear)
      
      nartyear = len(pipeyear)
      npipeyear = len(unique(pipeyear))
      ppipeyear = float(npipeyear) / nartyear
      
      narttot = len(pipetot[attmap])
      npipetot = len(unique(pipetot[attmap]))
      ppipetot = float(npipetot) / narttot

      result[attmap].append({
        'year' : year,
        'nartyear' : nartyear,
        'npipeyear' : npipeyear,
        'ppipeyear' : ppipeyear,
        'narttot' : narttot,
        'npipetot' : npipetot,
        'ppipetot' : ppipetot,
      })

  return result

def plotvar(var, dv='ppipeyear', outname=None):
  
  # Make data frame
  df = ro.DataFrame({
    'years' : ro.IntVector(qyear),
    'var' : ro.FloatVector([year[dv] for year in var]),
  })

  # Get y-label
  ylab = ''
  if dv.startswith('p'):
    ylab = 'Proportion'
  elif dv.startswith('n'):
    ylab = 'Count'

  # Get title
  title = ''
  if re.search('^\wpipe', dv):
    title = 'Pipeline Variability'
  elif re.search('^\wart', dv):
    title = 'Published Articles'

  # Make ggplot
  gp = ggplot2.ggplot(df) + \
    ggplot2.aes(x='years', y='var') + \
    ggplot2.stat_smooth(method='loess', formula='y~x', se=False, size=3) + \
    ggplot2.geom_point(stat='identity', size=5) + \
    ro.r.labs(y=ylab) + \
    ggplot2.opts(title=title)

  # Set font sizes
  gp += ro.r('opts(plot.title=theme_text(size=24))')
  gp += ro.r('opts(axis.title.x=theme_text(size=18))')
  gp += ro.r('opts(axis.text.x=theme_text(size=14))')
  gp += ro.r('opts(axis.title.y=theme_text(size=18, angle=90, vjust=0.33))')
  gp += ro.r('opts(axis.text.y=theme_text(size=14, angle=90))')

  # Hide x-label
  gp += ro.r('opts(axis.title.x=theme_blank())')

  # Draw ggplot
  gp.plot()

  # Save plot
  if outname:

    # Get save name
    savename = '%s/var/var-%s-%s.pdf' % (figdir, outname, dv)

    # Save to file
    # Include default dimensions to suppress ggsave output
    ro.r.ggsave(savename, height=7, width=7)

def getattrmap(src, incl=[], excl=[]):
  
  if incl:
    tags = incl
  else:
    tags = srclist[src]['src'].keys()
    if excl:
      tags = [tag for tag in tags if tag not in excl]

  attrs = [gettags(src, tag, rettype='attrib') for tag in tags]
  attrmap = dict(zip(tags, attrs))
  return attrmap

pulsemap = getattrmap('pulse')
procmap = getattrmap('proc')
techmap = getattrmap('tech')
magmap = getattrmap('mag')
modmap = getattrmap('mod')
mccmap = getattrmap('mcc')
pkgmap = getattrmap('pkg')

bigmap = dict(
  #pulsemap.items() + \
  procmap.items() + \
  #techmap.items() + \
  #magmap.items() + \
  modmap.items() + \
  mccmap.items() + \
  pkgmap.items()
)

def batchplotvar(var):
  
  plotvar(var['big'], dv='nartyear', outname='big')
  plotvar(var['big'], dv='npipeyear', outname='big')
  plotvar(var['big'], dv='ppipeyear', outname='big')

attmaps = {
  'pulse' : pulsemap,
  'proc' : procmap,
  'tech' : techmap,
  'mag' : magmap,
  'mod' : modmap,
  'mcc' : mccmap,
  'pkg' : pkgmap,
  'big' : bigmap,
}

def makedbfun(supname, tagname):
    
  return gettags(supname, tagname, rettype='attrib')

tagmap = {
  
  # Design
  'event' : makedbfun('des', 'event'),
  'block' : makedbfun('des', 'block'),
  'mixed' : makedbfun('des', 'mixed'),

  # Basis
  'hrf' : makedbfun('mod', 'hrf'),
  'tmpdrv' : makedbfun('mod', 'tmpdrv'),
  'dspdrv' : makedbfun('mod', 'dspdrv'),
  'fir' : makedbfun('mod', 'fir'),

  # Processing
  'evtopt' : makedbfun('proc', 'desopt'),
  'stc' : makedbfun('proc', 'stc'),
  'realign' : makedbfun('proc', 'realign'),
  'coreg' : makedbfun('proc', 'coreg'),
  'strip' : makedbfun('proc', 'strip'),
  'norm' : makedbfun('proc', 'norm'),
  'spatsmoo' : makedbfun('proc', 'spatsmoo'),
  'filter' : makedbfun('proc', 'filter'),
  'acf' : makedbfun('proc', 'autocorr'),
  'roi' : makedbfun('tech', 'roi'),
  'motreg' : makedbfun('proc', 'motreg'),
  
  # Multiple comparison correction
  'fdr' : makedbfun('mcc', 'fdr'),
  'bon' : makedbfun('mcc', 'bon'),
  'monte' : makedbfun('mcc', 'monte'),
  'rft' : gettags('mcc', 'rft', rettype='attrib') + \
          gettags('mcc', 'fwe', rettype='attrib'),

  # Software packages
  'spm' : makedbfun('pkg', 'spm'),
  'fsl' : makedbfun('pkg', 'fsl'),
  'afni' : makedbfun('pkg', 'afni'),
  'voyager' : makedbfun('pkg', 'voyager'),
  'freesurfer' : makedbfun('pkg', 'freesurfer'),

}

#for version in ['99', '2', '5', '8']:
#  tag_name = 'spm%s' % (version)
#  tagmap[tag_name] = {
#    'db' : gettags('pkg', 'spm', tagver=version, rettype='attrib') + \
#        gettags('pkg', 'spm', tagver=version+'b', rettype='attrib'),
#    'rep' : 'misc-softcom',
#    'repfun' : makecolfun('spm %s' % (version)),
#  }
