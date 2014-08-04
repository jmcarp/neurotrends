"""

"""

from neurotrends.config import re
from neurotrends.tagger import RexTagger, MultiRexTagger
from ..misc import delimiter, float_ptn, mov_ptn, cor_ptn

num_ptn = r'\d*\.?\d+'
mm_ptn = r'(mm|milli{dlm}met(er|re)s?)'.format(dlm=delimiter)
fw_ptn = r'(fwhm|full{dlm}width)'.format(dlm=delimiter)
hm_ptn = r'(fwhm|half{dlm}max(imum)?)'.format(dlm=delimiter)

power = RexTagger(
    'power',
    [
        r'power{dlm}analysis'.format(dlm=delimiter),
        r'power{dlm}calculation'.format(dlm=delimiter),
        r'sample{dlm}size{dlm}calculation'.format(dlm=delimiter),
    ]
)

desopt = RexTagger(
    'desopt',
    [
        r'design{dlm}optimi[sz]ation'.format(dlm=delimiter),
        r'optimization{dlm}of{dlm}experimental{dlm}design'.format(
            dlm=delimiter
        ),
        r'\Wm{dlm}sequence'.format(dlm=delimiter),
        r'optseq',
    ]
)

despike = RexTagger(
    'despike',
    [
        r'3ddespike',
        r'\Wde{dlm}spik'.format(dlm=delimiter),
    ]
)

winsor = RexTagger(
    'winsor',
    [
        r'wind?sori[sz]',
    ]
)

realign = RexTagger(
    'realign',
    [
        r'realign',
        r'{mov}{dlm}correct'.format(
            mov=mov_ptn,
            dlm=delimiter
        ),
        r'(motion|movement|translation|rotation){dlm}parameter'.format(
            dlm=delimiter,
        ),
        r'automat(ed|ic){dlm}image{dlm}registration'.format(dlm=delimiter),
        re.compile('\WAIR\W'),
        r'{cor}{dlm}(for)?{dlm}(bulk|whole|participants?|subjects?)?{dlm}(head)?{dlm}{mov}'.format(
            cor=cor_ptn,
            dlm=delimiter,
            mov=mov_ptn,
        ),
        r'{cor}{dlm}(for)?.{{,25}}and{dlm}(bulk|whole|participants?|subjects?)?{dlm}(head)?{dlm}{mov}'.format(
            cor=cor_ptn,
            dlm=delimiter,
            mov=mov_ptn,
        ),
        r'mcflirt',
        r'3dvolreg',
    ]
)

stc = RexTagger(
    'stc',
    [
        r'''
            slice{dlm}(scan)?{dlm}(acquisition)?{dlm}tim(e|ing){dlm}(and{dlm}{mov})?correct
        '''.format(
            dlm=delimiter,
            mov=mov_ptn,
        ),
        r'{cor}{dlm}for{dlm}(the)?{dlm}slice'.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'''
            {cor}[\w\s]{{,50}}tim(e|ing){dlm}differences{dlm}between{dlm}slice
        '''.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'''
            {cor}{dlm}for{dlm}differences{dlm}in{dlm}(the)?{dlm}slice{dlm}
                (scan)?{dlm}(acquisition)?{dlm}tim
        '''.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'''
            {cor}{dlm}for{dlm}(the)?{dlm}slice{dlm}(scan)?{dlm}tim(e|ing)
        '''.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'{cor}{dlm}for{dlm}acquisition{dlm}tim(e|ing)'.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'{cor}{dlm}for{dlm}{mov}and{dlm}slice'.format(
            cor=cor_ptn,
            dlm=delimiter,
            mov=mov_ptn,
        ),
        r'slice{dlm}dependent{dlm}(time|phase){dlm}shift'.format(dlm=delimiter),
        r'slicetimer',
        r'3dtshift',
        r'{cor}{dlm}for{dlm}non{dlm}simultaneous{dlm}slice'.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'{cor}[\w\s]{{,50}}asynchronous{dlm}slice'.format(
            cor=cor_ptn,
            dlm=delimiter,
        ),
        r'intra{dlm}session{dlm}(slice|volume){dlm}align'.format(
            dlm=delimiter
        ),
        # Calhoun et al., 2000
        r'''
            a{dlm}weighted{dlm}least{dlm}squares{dlm}algorithm{dlm}for{dlm}
                estimation{dlm}and{dlm}visualization{dlm}of{dlm}relative{dlm}
                latencies{dlm}in{dlm}event{dlm}related{dlm}functional
                {dlm}mri
        '''.format(dlm=delimiter),
        re.compile('\WTR{dlm}alignment'.format(dlm=delimiter)),
    ]
)

stc_context = MultiRexTagger(
    'stc',
    [
        # Ignore reslice, sliced, etc.
        r'\bslices?\b',
    ],
    [
        r'temporal(ly)?{dlm}align'.format(dlm=delimiter),
        r'sinc{dlm}interpolat'.format(dlm=delimiter),
        r'spline{dlm}interpolat'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*'
)

coreg = RexTagger(
    'coreg',
    [
        r'(co|cross)\-?regist(|er|ration)',
        r'cross{dlm}modal(ity)?{dlm}regist(er|ration)'.format(dlm=delimiter),
        r'''
            regist(er|ered|ration){dlm}(to|with).{{,25}}
                (functional|structural|anatomical|T1|EPI|
                image|volume|scan|brain)
        '''.format(dlm=delimiter),
    ]
)

strip = RexTagger(
    'strip',
    [
        r'skull{dlm}(was)?{dlm}strip'.format(dlm=delimiter),
        r'skull{dlm}(was)?{dlm}remov'.format(dlm=delimiter),
        re.compile('\WBET2?\W'),
        r'brain{dlm}extract'.format(dlm=delimiter),
        r'remov.{{,25}}non{dlm}brain'.format(dlm=delimiter),
        r'non{dlm}brain.{{,25}}remov'.format(dlm=delimiter),
        r'''
            brain{dlm}(tissues?)?{dlm}(and|from){dlm}
                non{dlm}brain
        '''.format(dlm=delimiter),
    ]
)

strip_context = MultiRexTagger(
    'strip',
    [r'skull'],
    [r'strip'],
    separator='[^.,:;?]*',
)

segment = RexTagger(
    'segment',
    [
        r'new{dlm}segment'.format(dlm=delimiter),
        re.compile('\WASEG\W'),
        r'fsl(\'s)?{dlm}fast'.format(dlm=delimiter),
        r'fast{dlm}segment'.format(dlm=delimiter),
        r'automated{dlm}segmentation'.format(dlm=delimiter),
        r'segmentation{dlm}(program|tool)'.format(dlm=delimiter),
        r'brain{dlm}(was)?{dlm}segment'.format(dlm=delimiter),
    ]
)

atlases = r'(standard|atlas|mni|talairach|template|reference|stereota)'

norm = RexTagger(
    'norm',
    [
        r'spatial(ly)?{dlm}normali'.format(dlm=delimiter),
        r'stereotactic(ally)?{dlm}normali'.format(dlm=delimiter),
        r'(normali[sz]|transform|regist|warp|conver).{{,25}}{atl}'.format(
            atl=atlases,
        ),
        r'fnirt',
        r'auto[\s\-_]*tlrc',
        r'3dwarp',
        r'\Wdartel\W',
        r'advanced{dlm}normalization'.format(dlm=delimiter),
        r'common{dlm}reference{dlm}space'.format(dlm=delimiter),
    ]
)

norm_primary = [
    r'normali',
    r'regist',
    r'transform',
    r'warp',
    r'align',
]

norm_context_v1 = MultiRexTagger(
    'norm',
    norm_primary,
    [
        r'template',
        r'atlas',
        r'stereota',
        r'talairach',
        r'mni',
        r'common{dlm}brain'.format(dlm=delimiter),
        r'standard{dlm}image'.format(dlm=delimiter),
        r'standard{dlm}space'.format(dlm=delimiter),
        r'montreal{dlm}neurological{dlm}institute'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*',
    nchar=150,
)

norm_context_v2 = MultiRexTagger(
    'norm',
    [
        r'(?<!intensity )normali',
    ],
    [
        r'realign',
        r'smooth',
    ],
    separator='[^.,:;?]*',
)

temporal_units = r'(s|seconds?)'

tempsmoo = RexTagger(
    'tempsmoo',
    [
        r'temporal(ly)?{dlm}smooth'.format(dlm=delimiter),
        r'temporal{dlm}gaussian'.format(dlm=delimiter),
        r'gaussian{dlm}temporal{dlm}filter'.format(dlm=delimiter),
        r'gaussian{dlm}temporal{dlm}kern[ea]l'.format(dlm=delimiter),
        r'\d{dlm}{units}{dlm}(fwhm|full{dlm}width|kern[ea]l|gauss)'.format(
            dlm=delimiter,
            units=temporal_units,
        ),
        r'fwhm[\s\-\)=:]*{flt}{dlm}{units}'.format(
            flt=float_ptn,
            dlm=delimiter,
            units=temporal_units,
        ),
        r'3dtsmooth',                        # 3dTsmooth [AFNI]
    ]
)

spatial_units = r'(mm|millimet(er|re)s?|voxels?|pixels?)'

spatsmoo = RexTagger(
    'spatsmoo',
    [
        r'spatial(ly)?{dlm}smooth'.format(dlm=delimiter),
        r'spatial{dlm}gaussian'.format(dlm=delimiter),
        r'gaussian{dlm}spatial{dlm}filter'.format(dlm=delimiter),
        r'gaussian{dlm}spatial{dlm}kern[ea]l'.format(dlm=delimiter),
        r'gaussian{dlm}spatial{dlm}blur'.format(dlm=delimiter),
        r'''
            \d{dlm}{unit}{dlm}
                (fwhm|full{dlm}width|kern[ea]l|gauss)
        '''.format(
            dlm=delimiter,
            unit=spatial_units,
        ),
        r'fwhm[\s\-\)=:]*{flt}{dlm}{unit}'.format(
            flt=float_ptn,
            dlm=delimiter,
            unit=spatial_units,
        ),
        r'isotropic{dlm}gaussian'.format(dlm=delimiter),
        r'gaussian{dlm}blur'.format(dlm=delimiter),
        r'smooth.{,25}?([^a-z]mm[^a-z]|millimet)',
    ]
)

spatsmoo_context = MultiRexTagger(
    'spatsmoo',
    [
        r'spatial(ly?){dlm}filter'.format(dlm=delimiter),
        r'gaussian(ly?){dlm}filter'.format(dlm=delimiter),
        r'smooth(ed|ing)',
    ],
    [
        # Match mm or mm3
        r'\Wmm3?\W',
        r'millimet(er|re)',
    ],
    nchar=150,
)

motreg = RexTagger(
    'motreg',
    [
        r'(motion|movement){dlm}regress'.format(dlm=delimiter),
        r'(motion|movement){dlm}parameter{dlm}regress'.format(dlm=delimiter),
        r'(motion|movement){dlm}co{dlm}variate'.format(dlm=delimiter),
    ]
)

motreg_primary = [
    # Negative look-ahead/behind for \w
    # Avoid [e]motion, translation[al]
    r'''
        \b
        (?<!eye\s)(?<!limb\s)
        (
            motion|movement|realignment|
            translation|rotation|roll|pitch|yaw
        )
        \b
    ''',
]

motreg_context = MultiRexTagger(
    'motreg',
    motreg_primary,
    [
        r'design\b',
        r'nuisance',
        r'covariate',
        r'regress',
        r'model',
        r'\bglm\b',
        r'account{dlm}for'.format(dlm=delimiter),
        r'residual{dlm}effects'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*',
)

motreg_context_strict = MultiRexTagger(
    'motreg',
    motreg_primary,
    [
        'included{dlm}in{dlm}(the)?{dlm}(design|model|glm)'.format(dlm=delimiter)
    ],
    separator='[^.]*',
)

filter = RexTagger(
    'filter',
    [
        r'''(pass|temporal){dlm}
            (butterworth|ha[mn]{{2}}ing|frequency)?{dlm}
            filter
        '''.format(dlm=delimiter),
        r'band{dlm}filter'.format(dlm=delimiter),
    ]
)

gscale = RexTagger(
    'gscale',
    [
        r'''
            (global|proportional)(ly)?{dlm}
                (signal)?{dlm}
                (scal|correct|adjust|control|regress)'
        '''.format(dlm=delimiter),
        r'''
            (scal|correct|adjust|control)(e|ed|ing)?{dlm}(for)?{dlm}
                (global|proportional){dlm}
                (signal|activ|drift|mean)
            '''.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}mode'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}mean'.format(dlm=delimiter),
    ]
)

autocorr = RexTagger(
    'autocorr',
    [
        r'\W(ar|auto{dlm}regressive){dlm}\(\d\)'.format(dlm=delimiter),
        r'temporal{dlm}auto{dlm}correlation'.format(dlm=delimiter),
        r'local{dlm}auto{dlm}correlation'.format(dlm=delimiter),
        r'intrinsic{dlm}auto{dlm}correlation'.format(dlm=delimiter),
        r'pre{dlm}whiten'.format(dlm=delimiter),
        r'auto{dlm}correlations?{dlm}(was|were){dlm}model'.format(dlm=delimiter),
        r'''
            whiten(ed|ing){dlm}
                (of)?{dlm}(the)?{dlm}
                (data|image|scans|functional)
        '''.format(dlm=delimiter),
    ]
)

estsmoo = RexTagger(
    'estsmoo',
    [
        r'3dfwhm',
        r'smoothness{dlm}estimat'.format(dlm=delimiter),
        r'estimat(e|ed|ing|ion){dlm}(of)?{dlm}(the)?smoothness'.format(dlm=delimiter),
    ]
)
