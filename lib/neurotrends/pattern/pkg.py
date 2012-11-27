cat = 'tool'

# Import base
from base import *

# Initialize tags
tags = {}

tags['spm'] = {
  'bool' : [
    '(?<!\w)spm(?!s)',
    'statistical%sparametric%smapping' % delimrep(2),
  ],
}

tags['fsl'] = {
  'bool' : [
    'fsl',
    'fmrib(?:\'s)?%ssoftware%slibrary' % delimrep(2),
  ],
}

tags['afni'] = {
  'bool' : [
    'afni',
    'analysis%sof%sfunctional%sneuroimages' % delimrep(3),
  ],
}

tags['suma'] = {
  'bool' : [
    '\Wsuma\W',
  ],
}

tags['voyager'] = {
  'bool' : [
    'brain%svoyager%s(?:2000|qx)?' % delimrep(2),
  ],
}

tags['medx'] = {
  'bool' : [
    '\Wmedx[^a-z]',
  ],
}

tags['surfer'] = {
  'bool' : [
    'freesurfer',
  ],
}

tags['caret'] = {
  'bool' : [
    'caret',
    'surefit',
    ('computerized%sanatomical%sreconstruction%s' + \
      'and%sediting%stoolkit') % delimrep(5),
  ],
}

tags['voxbo'] = {
  'bool' : [
    'voxbo',
  ],
}

tags['nipy'] = {
  'bool' : [
    'nipy(?:pe)?',
  ],
}

tags['pymvpa'] = {
  'bool' : [
    'pymvpa',
  ],
}

tags['cchips'] = {
  'bool' : [
    'cchips',
    'cincinnati%schildren\'s%shospital%simage%sprocessing%ssoftware' % 
      delimrep(5),
  ],
}

tags['lipsia'] = {
  'bool' : [
    'lipsia',
    'leipzig%simage%sprocessing%sand%sstatistical%sinference%salgorithm' % 
      delimrep(6),
  ],
}

tags['fmristat'] = {
  'bool' : [
    'fmristat\W',
  ],
}

tags['fmrlab'] = {
  'bool' : [
    'fmrlab',
  ],
}

tags['fiasco'] = {
  'bool' : [
    'fiasco',
  ],
}

tags['fidl'] = {
  'bool' : [
    'fidl',
  ],
}

tags['fiswidgets'] = {
  'bool' : [
    'fiswidgets',
  ],
}

################
# Add versions #
################

# Add SPM versions
spmvers = [
  '94', '96', '96b', '97', '99', '99b',
  '2', '2b', '5', '5b', '8', '8b'
]
spmnegbehind = ':\s'
spmnegahead = '[\w\-]'
tags['spm'] = makever('spm', tags['spm'], spmvers, 
  negbehind=spmnegbehind, negahead=spmnegahead)

# Add FSL versions
fslvers = [
  '1.0', '1.1', '1.3', '2.0', '3.0',
  '3.1', '3.2', '3.3', '4.0', '4.1',
  '4.1.0', '4.1.1', '4.1.2', '4.1.3', 
  '4.1.4', '4.1.5', '4.1.6', '4.1.7', 
  '4.1.8', '4.1.9'
]
fslarbptn = '(\d(?:\.\d){1,2})'
tags['fsl'] = makever('fsl', tags['fsl'], fslvers,
  escchars='.', arbptn=fslarbptn)

# Add AFNI versions
afnivers = [
  '2.2', '2.20b', '2.24', '2.24b', '2.29a', '2.31', '2.31b', 
  '2.51e', '2.51f', '2.51g', '2.51h', '2.51i', '2.51j', 
  '2.51k', '2.51m', '2.51n', '2.52a', '2.52b', '2.52c', 
  '2.52d', '2.52e', '2.52f', '2.52g', '2.52h', '2.52i', 
  '2.55a', '2.55d', '2.55h', '2.55i', '2.55j', '2.56a', 
  '2.56b', '2.56e',
]
afniarbptn = \
  '(?:' + \
    '(\d\.\d{2}[a-z]{0,1})' + \
    '|' + \
    '(?:afni_){0,1}(\d{4}_\d{2}_\d{2}_\d{4})' + \
  ')'
tags['afni'] = makever('afni', tags['afni'], afnivers,
  escchars='.', arbptn=afniarbptn)

# Add Freesurfer versions
fsvers = [
  '3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.0.4', '3.0.5', 
  '4.0.0', '4.0.1', '4.0.2', '4.0.3', '4.0.4', '4.0.5', 
  '4.1.0', '4.2.0', '4.3.0', '4.3.1', '4.4.0', '4.5.0', 
  '5.0.0', '5.1.0', '5.2.0',
]
fsarbptn = '(\d\.\d\.\d)'
tags['surfer'] = makever('surfer', tags['surfer'], fsvers,
  escchars='.', arbptn=fsarbptn)

# Add Brain Voyager versions
bvvers = [
  '1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', 
  '1.7', '1.8', '1.9', '2.0', '2.1', '2.2', '2.3', 
  '2.4', '3.5', '3.7', '3.9', '4.1', '4.4', '4.8',
]
bvarbptn = '(\d\.\d)'
tags['voyager'] = makever('voyager', tags['voyager'], bvvers,
  escchars='.', arbptn=bvarbptn)

