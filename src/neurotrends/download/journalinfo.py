import re
from htmlrules import *
from pdfrules import *

htmldefault = htmlfollow
pdfdefault = pdfdown

journalinfo = {
  'frontiers' : {
    'rule' : lambda url: re.search('frontiersin', url),
    'htmlmeth' : htmlfrontiers,
    'pdfmeth' : pdffrontiers,
  },
  'plos' : {
    'rule' : lambda url: re.search('plos', url),
    'htmlmeth' : htmlpass,
  },
  'scidir' : {
    'rule' : lambda url: re.search('sciencedirect', url),
    'htmlmeth' : htmlpass,
  },
  'oxford' : {
    'rule' : lambda url: re.search('oxford', url),
    'htmlmeth' : htmlpass,
  },
  'jamanet' : {
    'rule' : lambda url: re.search('jamanetwork', url),
    'htmlmeth' : htmlpass,
  },
  'jci' : {
    'rule' : lambda url: re.search('jci\.org', url),
    'htmlmeth' : htmlpass,
  },
  'bioscience' : {
    'rule' : lambda url: re.search('bioscience', url),
    'pdfmeth' : pdfbioscience,
  },
  'ymj' : {
    'rule' : lambda url: re.search('emyj', url),
    'htmlmeth' : htmlpass,
  },
  'bmj' : {
    'rule' : lambda url: re.search('bmj\.com', url),
    'htmlmeth' : htmlpass,
  },
  'aha' : {
    'rule' : lambda url: re.search('ahajournals', url),
    'htmlmeth' : htmlpass,
  },
  'medscimonit' : {
    'rule' : lambda url: re.search('medscimonit', url),
    'htmlmeth' : None,
    'pdfmeth' : pdfmedsci,
  },
  'jneuro' : {
    'rule' : lambda url: re.search('jneurosci', url),
    'htmlmeth' : htmlpass,
  },
  'nature' : {
    'rule' : lambda url: re.search('nature', url),
    'htmlmeth' : htmlnature,
    'pdfmeth' : pdfnature,
  },
  'apa' : {
    'rule' : lambda url: re.search('\.apa\.org', url),
    'htmlmeth' : htmlapa,
    'pdfmeth' : pdfapa,
  },
  'ama' : {
    'rule' : lambda url: re.search('ama\-assn', url),
    'htmlmeth' : htmlpass,
    'pdfmeth' : pdfama,
  },
  'wk' : {
    'rule' : lambda url: re.search('wkhealth', url),
    'htmlmeth' : htmlwk,
    'pdfmeth' : pdfwk,
  },
  'rsc' : {
    'rule' : lambda url: re.search('pubs\.rsc\.org', url),
    'htmlmeth' : htmlrsc,
  },
  'phys' : {
    'rule' : lambda url: re.search('physiology\.org', url),
    'htmlmeth' : htmlpass,
  },
  'neurology' : {
    'rule' : lambda url: re.search('\.neurology', url),
    'htmlmeth' : htmlpass,
  },
  'aacr' : {
    'rule' : lambda url: re.search('aacrjournals', url),
    'htmlmeth' : htmlpass,
  },
  'jove' : {
    'rule' : lambda url: re.search('jove', url),
    'htmlmeth' : htmlpass,
  },
  'psyonl' : {
    'rule' : lambda url: re.search('psychiatryonline', url),
    'htmlmeth' : htmlpass,
  },
  'snm' : {
    'rule' : lambda url: re.search('snmjournals', url),
    'htmlmeth' : htmlpass,
  },
  'jstage' : {
    'rule' : lambda url: re.search('jstage', url),
    'htmlmeth' : htmlpass,
  },
  'bmc' : {
    'rule' : lambda url: re.search('biomedcentral', url),
    'htmlmeth' : htmlpass,
  },
  'pnas' : {
    'rule' : lambda url: re.search('pnas', url),
    'htmlmeth' : htmlpass,
  },
  'iop' : {
    'rule' : lambda url: re.search('iop\.org', url),
    'htmlmeth' : htmlpass,
  },
  'bbf' : {
    'rule' : lambda url: re.search('behavioralandbrainfunctions', url),
    'htmlmeth' : htmlpass,
  },
}
