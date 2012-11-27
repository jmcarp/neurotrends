cat = 'analysis'

# Import base 
from base import *

# Check slice-timing correction
priptn_stc = [
  'slice',
]
secptn_stc = [
  'temporal%salignment' % (delimptn),
  'temporally%salign' % (delimptn),
  'sinc%sinterpolat' % (delimptn),
  'spline%sinterpolat' % (delimptn),
]
def checkstc(txt, **conargs):
  return contextsearch(txt, priptn_stc, secptn_stc, ichar='.', **conargs)

# Check skull-stripping
priptn_strip = [
  'skull',
]
secptn_strip = [
  'strip',
]
def checkstrip(txt, **conargs):
  return contextsearch(txt, priptn_strip, secptn_strip, ichar='.', **conargs)

# Check head motion regression
priptn_motreg = [
  # Negative look-ahead/behind for \w
  # Avoid [e]motion, translation[al]
  '(?<!\w)(?<!eye )(?<!limb )(?:motion|movement|realignment|translation|rotation|roll|pitch|yaw)(?!\w)',
]
secptn_motreg = [
  'design(?!\w)',
  'nuisance',
  'covariate',
  'regress',
  'model',
  '(?<!\w)glm(?!\w)',
]
secptn_motreg_strict = [
  'included%sin%sthe%s(?:design|model|glm)' % delimrep(3),
]
def checkmotreg(txt, **conargs):
  return contextsearch(txt, priptn_motreg, secptn_motreg, ichar='.,:;?', **conargs)
def checkmotreg_strict(txt, **conargs):
  return contextsearch(txt, priptn_motreg, secptn_motreg_strict, ichar='.', **conargs)

# Check normalization
priptn_norm = [
  'normali',
  'regist',
  'transform',
  'warp',
  're%sampl' % (delimptn),
]
secptn_norm = [
  'template',
  'atlas',
  'stereota',
  'talairach',
  'mni',
  'standard%simage' % (delimptn),
  'standard%sspace' % (delimptn),
  'montreal%sneurological%sinstitute' % delimrep(2),
]
def checknorm(txt, **conargs):
  return contextsearch(txt, priptn_norm, secptn_norm, ichar='.', **conargs)
def checknorm_context(txt, **conargs):
  return contextsearch(txt, ['(?<!intensity )normali'], ['realign', 'smooth'], ichar='.', **conargs)

# Initialize tags
tags = {}

tags['power'] = [
  'power%sanalysis' % (delimptn),
  'power%scalculation' % (delimptn),
  'sample%ssize%scalculation' % delimrep(2),
]

tags['desopt'] = [
  'design%soptimi[sz]ation' % delimrep(1),
  'optimization%sof%sexperimental%sdesign' % delimrep(3),  # Wager GA reference
  '\Wm%ssequence' % delimrep(1),                           # M-sequence optimization
  'optseq',                                                # OptSeq program
]

tags['despike'] = [
  '3ddespike',                  # AFNI 3dDespike program
  '\Wde%sspik' % (delimptn),
]

tags['winsor'] = [
  'wind?sori[sz]',
]

tags['realign'] = [
  'realign',
  '%s%scorrect' % (movptn, delimptn),
  '(?:motion|movement|translation|rotation)%sparameter' % (delimptn),
  'automat(?:ed|ic)%simage%sregistration' % delimrep(2),    # AIR
  re.compile('\WAIR\W'),                                    # AIR
  '%s%s(?:for)?%s(?:subject)?%s(?:head)?%s%s' % \
    ((corptn,) + delimrep(4) + (movptn,)),
  '%s%s(?:for)?.{,25}and%s(?:subject)?%s(?:head)?%s%s' % \
    ((corptn,) + delimrep(4) + (movptn,)),
  'mcflirt',                                                # MCFLIRT [FSL]
  '3dvolreg',                                               # 3dvolreg [AFNI]
]

tags['stc'] = [
  'slice%s(?:scan)?%s(?:acquisition)?%stim(?:e|ing)%scorrect' % delimrep(4),
  '%s%sfor%s(?:the)?%sslice' % ((corptn,) + delimrep(3)),
  '%s%sfor%stim(?:e|ing)%sdifferences%sbetween%sslice' % ((corptn,) + delimrep(5)),
  '%s%sfor%sdifferences%sin%s(?:the)?%sslice%s(?:scan)?%s(?:acquisition)?%stim' \
    % ((corptn,) + delimrep(8)),
  '%s%sfor%s(?:the)?%sslice%s(?:scan)?%stim(?:e|ing)' % ((corptn,) + delimrep(5)),
  '%s%sfor%sacquisition%stim(?:e|ing)' % ((corptn,) + delimrep(3)),
  '%s%sfor%s%sand%sslice' % (corptn, delimptn, delimptn, movptn, delimptn,),
  'slice%sdependent%stime%sshift' % delimrep(3),
  'slicetimer',           # slicetimer [FSL]
  '3dtshift',             # 3dTshift [AFNI]
  '%s%sfor%snon%ssimultaneous%sslice' % ((corptn,) + delimrep(4)),
  '%s%sfor%sasynchronous%sslice' % ((corptn,) + delimrep(3)),
  'intra%ssession%s(?:slice|volume)%salign' % delimrep(3),
  # Calhoun et al., 2000
  ('a%sweighted%sleast%ssquares%salgorithm%sfor%sestimation%s' + \
    'and%svisualization%sof%srelative%slatencies%sin%sevent%s' + \
    'related%sfunctional%smri') % delimrep(16),
  re.compile('\WTR%salignment' % (delimptn)),
  checkstc,
]

tags['coreg'] = [
  '(?:co|cross)\-?regist(?:|er|ration)',
  'cross%smodal(?:ity)?%sregist(?:er|ration)' % delimrep(2),
  'regist(?:er|ered|ration)%s(?:to|with).{,25}(?:functional|structural|anatomical|T1|EPI|image|volume|scan|brain)' % delimrep(1),
]

tags['strip'] = [
  'skull%s(?:was)?%sstrip' % delimrep(2),
  'skull%s(?:was)?%sremov' % delimrep(2),
  re.compile('\WBET2?\W'),      # BET [FSL]
  'brain%sextract' % delimrep(1),
  'remov.{,25}non%sbrain' % delimrep(1),
  'non%sbrain.{,25}remov' % (delimptn),
  'brain%s(?:tissues?)?%s(?:and|from)%snon%sbrain' % delimrep(4),
  checkstrip,
]

tags['segment'] = [
  'new%ssegment' % (delimptn),    # New Segment [SPM]
  re.compile('\WASEG\W'),         # ASEG [FreeSurfer]
  'fsl(?:\'s)?%sfast' % delimrep(1),
  'fast%ssegment' % delimrep(1),
  'automated%ssegmentation' % delimrep(1),
  'segmentation%s(?:program|tool)' % delimrep(1),
  'brain%s(?:was)?%ssegment' % delimrep(2),
]

tags['norm'] = [
  'spatial(?:ly)?%snormali' % (delimptn),
  'stereotactic(?:ally)?%snormali' % (delimptn),
  '(?:normali[sz]|transform|regist|warp|conver).{,25}(?:standard|atlas|mni|talairach|template|reference|stereota)',
  'fnirt',                                  # FNIRT [FSL]
  'auto[\s\-_]*tlrc',                       # auto_tlrc [AFNI]
  '3dwarp',                                 # 3dWarp [AFNI]
  '\Wdartel\W',                             # DARTEL [SPM]
  'advanced%snormalization' % delimrep(1),  # ANTS
  'common%sreference%sspace' % delimrep(2),
  checknorm,
  checknorm_context,
]

tags['tempsmoo'] = [
  'temporal(?:ly)?%ssmooth' % (delimptn),
  'temporal%sgaussian' % (delimptn),
  'gaussian%stemporal%sfilter' % delimrep(2),
  'gaussian%stemporal%skern[ea]l' % delimrep(2),
  '\d%s(?:s|seconds?)%s(?:fwhm|full%swidth|kern[ea]l|gauss)' % delimrep(3),
  'fwhm[\s\-\)=:]*%s%s(?:s|seconds?)' % (floatptn, delimptn),
  '3dtsmooth',            # 3dTsmooth [AFNI]
]

tags['spatsmoo'] = [
  'spatial(?:ly)?%ssmooth' % (delimptn),
  'spatial%sgaussian' % (delimptn),
  'gaussian%sspatial%sfilter' % delimrep(2),
  'gaussian%sspatial%skern[ea]l' % delimrep(2),
  'gaussian%sspatial%sblur' % delimrep(2),
  '\d%s(?:mm|millimeters?|voxels?|pixels?)%s(?:fwhm|full%swidth|kern[ea]l|gauss)' % delimrep(3),
  'fwhm[\s\-\)=:]*%s%s(?:mm|millimeters?|voxels?|pixels?)' % (floatptn, delimptn),
  'isotropic%sgaussian' % (delimptn),
  'gaussian%sblur' % delimrep(1),
]

tags['motreg'] = [
  '(?:motion|movement)%sregress' % delimrep(1),
  '(?:motion|movement)%sparameter%sregress' % delimrep(2),
  '(?:motion|movement)%sco%svariate' % delimrep(2),
  '(?:account%sfor|model)%s(?:any)?%sresidual%seffects%s(?:of|related%sto)%s(?:head)?%s(?:motion|movement)' % delimrep(8),
  checkmotreg,
  checkmotreg_strict,
]

tags['filter'] = [
  '(?:pass|temporal)%s(?:butterworth|ha[mn]{2}ing|frequency)?%sfilter' % delimrep(2),
  'band%sfilter' % (delimptn),
]

tags['gscale'] = [
  '(?:global|proportional)(?:ly)?%s(?:signal)?%s(?:scal(?:e|ing)|correct|adjust|control|regress)' 
    % delimrep(2),
  '(?:scal|correct|adjust|control)(?:e|ed|ing)?%sfor%s(?:global|proportional)%s(signal|activ(?:ation|ivity)|drift|mean)' 
    % delimrep(3),
  'whole%sbrain%smode' % delimrep(2),
  'whole%sbrain%smean' % delimrep(2),
]

tags['autocorr'] = [
  '\W(?:ar|auto%sregressive)%s\(\d\)' % delimrep(2),
  'temporal%sauto%scorrelation' % delimrep(2),
  'local%sauto%scorrelation' % delimrep(2),
  'intrinsic%sauto%scorrelation' % delimrep(2),
  'pre%swhiten' % (delimptn),
  'auto%scorrelations?%s(?:was|were)%smodel' % delimrep(3),
  'whiten(?:ed|ing)%s(?:of)?%s(?:the)?%s(?:data|image|scans|functional)' % delimrep(3),
]

tags['estsmoo'] = [
    '3dfwhm',                   # 3dFWHM [AFNI]
    'smoothness.{,15}estimat',
    'estimat(?:e|ed|ing|ion)%s(?:of)?%s(?:the)?smoothness' % delimrep(2),
]

