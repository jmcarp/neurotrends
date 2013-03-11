
# 
import re
from scipy.stats import norm

# Import fmri-report
import sys
sys.path.append('/Users/jmcarp/Dropbox/projects/fmri-report/scripts')
import reportproc as rp

# Import project modules
from tagplot import *

# NLTK imports
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

def preproc(art):
  """
  Extract a cleaned list of tokens from an Article.
  """
  
  html = loadhtml(art)
  pdf = loadpdf(art)

  text = html + ' ' + pdf

  # Lower-case
  text = text.lower()

  # Remove extra <script> tags
  text = re.sub('<script>.*?</script>', '', text)

  # Tokenize
  tokens = nltk.word_tokenize(text)

  # Remove stop-words
  tokens = [
    t for t in tokens 
    if t not in stopwords.words('english') 
    and len(t) > 2
    and re.search('[a-z]+', t)
  ]

  return tokens

def articles_to_mallet(outname, method):
  
  # Open output file
  if method == 'onefile':
    outfile = open(outname, 'w')

  # Read report
  report = rp.ezread()
  
  # Get articles in both report and NeuroTrends
  arts = [
    art for art in report
    if art['proc-slicetime-bool'] in ['TRUE', 'FALSE', 'missing']
    and session.query(Article).filter(Article.pmid == art['pmid']).count()
  ]
  
  # Initialize return list
  out = []

  # Process articles
  for art in arts:
    
    print 'Working on article %s...' % (art['pmid'])

    # Get tokens
    tokens = preproc(toart(art['pmid']))
    
    # Skip if no tokens found
    if not tokens:
      continue
    
    # Write PMID, label, and tokens to output file
    if method == 'onefile':
      outrow = [art['pmid'], art['proc-slicetime-bool']] + tokens
      outtext = ' '.join(outrow)
      outtext = outtext.encode('ascii', 'ignore')
      outfile.write(outtext)
    elif method == 'manyfiles':
      outpath = '%s/%s' % (outname, art['proc-slicetime-bool'])
      if not os.path.exists(outpath):
        os.makedirs(outpath)
      outfile = open('%s/%s.txt' % (outpath, art['pmid']), 'w')
      outtext = ' '.join(tokens)
      outtext = outtext.encode('ascii', 'ignore')
      outfile.write(outtext)
      outfile.close()

    out.append({
      'pmid' : art['pmid'],
      'stc' : art['proc-slicetime-bool'],
      'tokens' : ' '.join(tokens),
    })

  # Close output file
  if method == 'onefile':
    outfile.close()

  return out

def makecolfun(ptn):
  
  fun = lambda txt: bool(re.search(ptn, txt, re.I))
  return fun

def maketaginfo(supname, tagname, colname, colptn=None):

  info = {
    'db' : gettags(supname, tagname, rettype='attrib'),
    'rep' : colname,
  }

  if colptn:
    info['repfun'] = makecolfun(colptn)

  return info

tagmap = {
  
  # Design
  'event' : maketaginfo('des', 'event', 'des-edes-destype', colptn='event'),
  'block' : maketaginfo('des', 'block', 'des-edes-destype', colptn='block'),
  'mixed' : maketaginfo('des', 'mixed', 'des-edes-destype', colptn='mixed'),

  # Basis
  'hrf' : maketaginfo('mod', 'hrf', 'mod-smod-basis', colptn='hrf'),
  'tmpdrv' : maketaginfo('mod', 'tmpdrv', 'mod-smod-basis', colptn='td'),
  'dspdrv' : maketaginfo('mod', 'dspdrv', 'mod-smod-basis', colptn='disp'),
  'fir' : maketaginfo('mod', 'fir', 'mod-smod-basis', colptn='fir'),

  # Processing
  'evtopt' : maketaginfo('proc', 'desopt', 'des-edes-eventopt-optmethod'),
  'stc' : maketaginfo('proc', 'stc', 'proc-slicetime-bool'),
  'realign' : maketaginfo('proc', 'realign', 'proc-mc-bool'),
  'coreg' : maketaginfo('proc', 'coreg', 'proc-coreg-bool'),
  'strip' : maketaginfo('proc', 'strip', 'proc-skullstrip-bool'),
  'norm' : maketaginfo('proc', 'norm', 'proc-norm-bool'),
  'spatsmoo' : maketaginfo('proc', 'spatsmoo', 'proc-smooth-bool'),
  'filter' : maketaginfo('proc', 'filter', 'mod-smod-filter-bool'),
  'acf' : maketaginfo('proc', 'autocorr', 'mod-smod-acf-bool'),
  'roi' : maketaginfo('tech', 'roi', 'mod-roi-bool'),
  'motreg' : maketaginfo('proc', 'motreg', 'mod-smod-regress', colptn='movement params'),
  
  # Multiple comparison correction
  'fdr' : maketaginfo('mcc', 'fdr', 'mod-gmod-mccorrect-mccmethod', 
    colptn='fdr'),
  'bon' : maketaginfo('mcc', 'bon', 'mod-gmod-mccorrect-mccmethod',
    colptn='bonferroni'),
  'monte' : maketaginfo('mcc', 'monte', 'mod-gmod-mccorrect-mccmethod', 
    colptn='(monte carlo|alphasim)'),
  'rft' : {
    'db' : gettags('mcc', 'rft', rettype='attrib') +
           gettags('mcc', 'fwe', rettype='attrib'),
    'rep' : 'mod-gmod-mccorrect-mccmethod',
    'repfun' : makecolfun('fwe|rft'),
  },

  # Software packages
  'spm' : maketaginfo('pkg', 'spm', 'misc-softpck', 
    colptn='spm'),
  'fsl' : maketaginfo('pkg', 'fsl', 'misc-softpck', 
    colptn='fsl'),
  'afni' : maketaginfo('pkg', 'afni', 'misc-softpck', 
    colptn='afni'),
  'voyager' : maketaginfo('pkg', 'voyager', 'misc-softpck', 
    colptn='voyager'),
  'freesurfer' : maketaginfo('pkg', 'freesurfer', 'misc-softpck', 
    colptn='freesurfer'),

  # Task packages
  'eprime' : maketaginfo('task', 'eprime', 'des-edes-taskprog',
    colptn='eprime'),
  'presentation' : maketaginfo('task', 'presentation', 'des-edes-taskprog',
    colptn='presentation'),
  'cogent' : maketaginfo('task', 'cogent', 'des-edes-taskprog',
    colptn='cogent'),
  'psyscope' : maketaginfo('task', 'psyscope', 'des-edes-taskprog',
    colptn='psyscope'),
  'psychtoolbox' : maketaginfo('task', 'psychtoolbox', 'des-edes-taskprog',
    colptn='psychtoolbox'),

}

for version in ['99', '2', '5', '8']:
  tag_name = 'spm%s' % (version)
  tagmap[tag_name] = {
    'db' : gettags('pkg', 'spm', tagver=version, rettype='attrib') + \
        gettags('pkg', 'spm', tagver=version+'b', rettype='attrib'),
    'rep' : 'misc-softcom',
    'repfun' : makecolfun('spm %s' % (version)),
  }

truth_map = {
  'TRUE' : True,
  'FALSE': False,
  'missing' : False,
  'n/a' : False,
}

def validate(check_method='db'):
  
  # Read article report
  report = rp.ezread()
  
  articles = []
  results = {}

  for rep_article in report:
    
    # Get PubMed ID
    pmid = rep_article['pmid']

    print 'Working on article %s...' % (pmid)
    
    # Get article from database
    db_article = session.query(Article)\
      .filter(Article.pmid==pmid)\
      .first()
    
    # Continue if article not found
    if not db_article:
      continue
    
    if check_method == 'files':

      # Read files
      htmltxt = loadhtml(db_article)
      pdftxt = loadpdf(db_article)
      
      # Continue if files not found
      if not htmltxt and not pdftxt:
        continue

    elif check_method == 'db':
      
      # Continue if files not in database
      if not db_article.htmlfile and not db_article.pdfrawfile:
        continue

    print 'Found article %s...' % (pmid)
    
    articles.append(pmid)

    for tagname in tagmap:
      
      # Get tag info
      tag = tagmap[tagname]
      
      # Continue if database attrib not found
      if not tag['db']:
        continue

      # Get database value
      db_tag = any([attrib in db_article.attribs for attrib in tag['db']])

      # Get report value
      rep_tag = rep_article[tag['rep']]
      if 'repfun' in tag:
        rep_tag = tag['repfun'](rep_tag)
      else:
        if rep_tag in truth_map:
          rep_tag = truth_map[rep_tag]
        else:
          rep_tag = True
      
      if tagname not in results:
        results[tagname] = []

      results[tagname].append((db_tag, rep_tag))
  
  # Summarize results
  summary = {}

  for tagname in results.keys():
    
    tp = len([res for res in results[tagname] if res == (True, True)])
    fp = len([res for res in results[tagname] if res == (True, False)])
    fn = len([res for res in results[tagname] if res == (False, True)])
    tn = len([res for res in results[tagname] if res == (False, False)])

    phit = float(tp) / (tp + fn)
    if phit == 0:
      phit = 0.001
    elif phit == 1:
      phit = 1 - 0.001
    pfal = float(fp) / (tn + fp)
    if pfal == 0:
      pfal = 0.001
    elif pfal == 1:
      pfal = 1 - 0.001
    dp = norm.ppf(phit) - norm.ppf(pfal)

    summary[tagname] = {
      'tp' : tp,
      'fp' : fp,
      'fn' : fn,
      'tn' : tn,
      'phit' : phit,
      'pfal' : pfal,
      'dp' : dp,
    }
    
  return articles, results, summary

def batchplotvalidate(summary):
  
  plotstat(summary, 'dp', "d'", saveplot=True)
  plotstat(summary, 'phit', 'Proportion Hits', saveplot=True)
  plotstat(summary, 'pfal', 'Proportion False Alarms', saveplot=True)

def plotstat(summary, statname, statlong='', saveplot=False):
  
  if not statlong:
    statlong = statname

  stat = [summary[s][statname] for s in summary]
  df = ro.DataFrame({
    'stat' : ro.FloatVector(stat),
  })

  gp = ggplot2.ggplot(df) + \
    ggplot2.aes(x='stat') + \
    ggplot2.geom_histogram() + \
    ggplot2.opts(title='Validation Performance') + \
    ro.r.labs(x=statlong, y='Count')

  # Set font sizes
  gp += ro.r('opts(plot.title=theme_text(size=24))')
  gp += ro.r('opts(axis.title.x=theme_text(size=18))')
  gp += ro.r('opts(axis.text.x=theme_text(size=14))')
  gp += ro.r('opts(axis.title.y=theme_text(size=18, angle=90, vjust=0.33))')
  gp += ro.r('opts(axis.text.y=theme_text(size=14, angle=90))')

  gp.plot()

  if saveplot:
    ro.r.ggsave('%s/misc/%s.pdf' % (figdir, statname))
