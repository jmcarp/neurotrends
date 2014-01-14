from neurotrends.config import re
from neurotrends.tagger import rex_compile, rex_flex, rex_ctx, rex_named
from neurotrends.tagger import CustomTagger
from ..misc import delimiter, float_ptn

# S or Hz not followed by numbers
# To avoid s-1 units
hpf_unit_ptn = ur'''
    (
        s(ec(onds?)?)?
        |
        hz
    )
    (?!\w)
    (?!\s*\d)
'''

highpass_filter_bool_ptn = [
    rex_compile(ptn)
    for ptn in [
        r'high{dlm}pass'.format(dlm=delimiter)
    ]
]

highpass_filter_neg_ptn = [
    rex_compile(ptn)
    for ptn in [
        r'stimul(i|us)',
        r'gaussian',
        r'half{dlm}max'.format(dlm=delimiter),
        r'low{dlm}pass'.format(dlm=delimiter),
        r'temporal(ly)?{dlm}smooth'.format(dlm=delimiter),
        r'smooth(ed|ing)?{dlm}temporal'.format(dlm=delimiter),
    ]
]

highpass_filter_wide_neg_ptn = [
    rex_compile(ptn)
    for ptn in [
        # Skip on patterns related to non-fMRI signals (EEG, NIRS, etc.)
        r'\beeg\b',
        r'\berp\b',
        r'\bmeg\b',
        r'\blfp\b',
        r'\bemg\b',
        r'\beog\b',
        r'\bgfp\b',
        r'\bf?nirs\b',
        r'\bvep\b',
        r'ssvep',
        r'mastoid',
        r'amplifi',
        r'electrode',
        r'alpha',
        r'beta',
        r'delta',
        r'gamma',
        r'vocal',
        r'word',
    ]
]

highpass_filter_values_fraction = rex_compile(
    ur'(?<![\d\-\u2212]\s){num1}{dlm}[/\u2044]{dlm}{num2}{dlm}{unit}'.format(
        dlm=delimiter,
        num1=rex_named(float_ptn, 'num'),
        num2=rex_named(float_ptn, 'dnm'),
        unit=rex_named(hpf_unit_ptn, 'units'),
    )
)
highpass_filter_values = rex_compile(
    ur'(?<![\d\-\u2212]\s){num}{dlm}{unit}'.format(
        dlm=delimiter,
        num=rex_named(float_ptn, 'cutoff'),
        unit=rex_named(hpf_unit_ptn, 'units'),
    )
)

highpass_filter_bool_ptn = [
    rex_compile(ptn)
    for ptn in highpass_filter_bool_ptn
]

def est_highpass_cutoff(txt):
    """

    """
    cutoffs = []

    ctxt = re.sub('[():=]', '', txt)

    for ptn in highpass_filter_bool_ptn:

        matches = rex_flex(ptn, ctxt, re.finditer)

        for match in matches:

            context, span = rex_ctx(match, ctxt)

            # Skip if negative patterns match
            stop = False
            for neg_ptn in highpass_filter_neg_ptn:
                if rex_flex(neg_ptn, context):
                    stop = True
                    break
            if stop:
                continue

            # Skip if wide-range negative patterns match
            context_wide, _ = rex_ctx(match, ctxt, nchar=500)
            for neg_ptn in highpass_filter_wide_neg_ptn:
                if rex_flex(neg_ptn, context_wide):
                    stop = True
                    break
            if stop:
                continue

            context_search, _ = rex_ctx(match, ctxt, nchar_pre=0)

            # Match on fraction pattern (e.g. 1 / 128 Hz)
            matches = rex_flex(
                highpass_filter_values_fraction, context_search,
                fun=re.finditer
            )
            matches = list(matches)

            if len(matches) == 1:

                match = matches[0]
                group = match.group()

                numerator = match.groupdict()['num']
                denominator = match.groupdict()['dnm']

                if (numerator.startswith('0') and not numerator.startswith('0.')) or \
                        (denominator.startswith('0') and not denominator.startswith('0.')):
                    continue

                try:
                    numerator = float(numerator)
                    denominator = float(denominator)
                except (ValueError, TypeError):
                    continue

                # Avoid zero-division errors
                if numerator == 0 or denominator == 0:
                    continue

                cutoff = numerator / denominator

                units = match.groupdict()['units']
                if units.lower() == 'hz':
                    cutoff = 1 / cutoff

                cutoffs.append({
                    'value': cutoff,
                    'context': context,
                    'group': group,
                    'span': span,
                })

                # Stop if fraction matches
                continue

            # Match on single-value pattern (e.g. 0.05 Hz)
            matches = rex_flex(
                highpass_filter_values, context_search, fun=re.finditer
            )
            matches = list(matches)

            if len(matches) == 1:

                match = matches[0]
                group = match.group()

                cutoff = match.groupdict()['cutoff']

                if cutoff.startswith('0') and not cutoff.startswith('0.'):
                    continue

                try:
                    cutoff = float(cutoff)
                except (ValueError, TypeError):
                    continue

                if cutoff == 0:
                    continue

                units = match.groupdict()['units']
                if units.lower() == 'hz':
                    cutoff = 1 / cutoff

                cutoffs.append({
                    'value': cutoff,
                    'context': context,
                    'group': group,
                    'span': span,
                })

    return cutoffs

highpass_cutoff = CustomTagger('highpass_cutoff', est_highpass_cutoff)
