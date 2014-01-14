from neurotrends.config import re
from neurotrends.tagger import rex_compile, rex_flex, rex_ctx, rex_named
from neurotrends.tagger import CustomTagger
from ..misc import delimiter, float_ptn

mm_ptn = r'(mm|milli{dlm}met(er|re)s?)'.format(dlm=delimiter)
fw_ptn = r'(fwhm|full{dlm}width)'.format(dlm=delimiter)
hm_ptn = r'(fwhm|half{dlm}max(imum)?)'.format(dlm=delimiter)

smooth_spatial_ptn = [
    r'{num}{dlm}{mm}{dlm}{fw}'.format(
        num=rex_named(float_ptn, 'kernel'),
        mm=mm_ptn,
        fw=fw_ptn,
        dlm=delimiter,
    ),
    r'''
        {halfmax}{dlm}
        (of|at|(set{dlm}to)|(equal{dlm}to))?{dlm}
        ({num}){dlm}{mm}
    '''.format(
        dlm=delimiter,
        halfmax=hm_ptn,
        num=rex_named(float_ptn, 'kernel'),
        mm=mm_ptn,
    )
]
smooth_spatial_ptn = [
    rex_compile(ptn) for ptn in smooth_spatial_ptn
]

MAX_FWHM = 30

def est_smooth_kernel(txt):

    # Initialize FWHM
    kernels = []

    ctxt = re.sub(r'[():=]', '', txt)

    for ptn in smooth_spatial_ptn:

        matches = rex_flex(ptn, ctxt, re.finditer)

        for match in matches:

            kernel_str = match.groupdict()['kernel']

            # Handle ...
            six_match = re.search('(\d+?)6(\d+?)6(\d+)', kernel_str)
            if six_match:
                if len(set(six_match.groups())) == 1:
                    kernel_str = six_match.groups()[-1]

            # Skip if match preceded by number; prevents matches on input like
            # "6 .5 mm fwhm"
            context_back, _ = rex_ctx(match, ctxt, nchar_pre=10, nchar_post=0)
            before_group = context_back.replace(match.group(), '')
            if re.search(r'[.\d]\s+$', before_group):
                continue

            # Skip if not float
            try:
                kernel = float(kernel_str)
            except (ValueError, TypeError):
                continue

            # Skip if implausible
            if kernel > MAX_FWHM:
                continue

            context, span = rex_ctx(match, ctxt)
            group = match.group()
            kernels.append({
                'value': kernel,
                'context': context,
                'group': group,
                'span': span,
            })

    return kernels

smooth_kernel = CustomTagger('smooth_kernel', est_smooth_kernel)
