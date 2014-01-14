from neurotrends.config import re
from neurotrends.tagger import rex_compile, rex_named, rex_flex, rex_ctx
from neurotrends.tagger import CustomTagger
from ..misc import delimiter

MIN_FIELD_STRENGTH = 0.5
MAX_FIELD_STRENGTH = 12

# Magnet patterns
vend_ptn = r'siemens|philips|general{dlm}electric|\Wge\W'.format(dlm=delimiter)
scan_ptn = r'magnet|scan(ner)?|mri|field|system'
mag_ptn = r'({vend}|{scan})'.format(vend=vend_ptn, scan=scan_ptn)

tesla_ptn = r'(tesla|t(?!\w|{dlm}=|{dlm}\d+|\())'.format(dlm=delimiter)
num_ptn = r'[\s\(](\d{1,2}\.?\d{,2})(?!=\d)'

field_ptn = [
    rex_compile(rex_named(num_ptn, 'field') + delimiter + tesla_ptn),
]

sig_ptn = 'p{dlm}[<=>]+{dlm}\d?\.\d+'.format(dlm=delimiter)
sig_ptn = rex_compile(sig_ptn)

def est_field_strength(txt):

    fields = []

    for ptn in field_ptn:

        matches = rex_flex(ptn, txt, fun=re.finditer)

        for match in matches:

            short_context, _ = rex_ctx(match=match, txt=txt, nchar=50)

            if not re.search(mag_ptn, short_context, re.I):
                continue

            # Skip if significance test; easy to confuse with e.g.
            # "3.0 T, p < 0.05"
            post_context, _ = rex_ctx(match, txt, nchar_pre=0, nchar_post=50)
            if rex_flex(sig_ptn, post_context):
                continue

            field_str = match.groupdict()['field']

            # Try to cast field strength to float
            try:
                field = float(field_str)
            except (ValueError, TypeError):
                continue

            if MIN_FIELD_STRENGTH <= field <= MAX_FIELD_STRENGTH:

                context, span = rex_ctx(match, txt)
                group = match.group()

                fields.append({
                    'value': field,
                    'context': context,
                    'group': group,
                    'span': span,
                })

    return fields

field_strength = CustomTagger('field_strength', est_field_strength)
