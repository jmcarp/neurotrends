import functools

from neurotrends.config import re

REX_TYPE = type(re.compile(''))
DEF_FLAGS = re.IGNORECASE | re.VERBOSE
NCHAR = 50
UNKNOWN_VERSION = '?'


def rex_wrap(rex, wrap=''):
    return ur'({wrap}{rex})'.format(rex=rex, wrap=wrap)


def rex_named(rex, name):
    return rex_wrap(rex, '?P<{}>'.format(name))


rex_noncap = functools.partial(rex_wrap, wrap='?:')
rex_posbehind = functools.partial(rex_wrap, wrap='?<=')
rex_negbehind = functools.partial(rex_wrap, wrap='?<!')
rex_posahead = functools.partial(rex_wrap, wrap='?=')
rex_negahead = functools.partial(rex_wrap, wrap='?!')


# TODO: Only keep earliest tags
def uextend(base, vals):
    for val in vals:
        if val not in base:
            base.append(val)


def first_match(tags):
    return sorted(tags, key=lambda tag: sum(tag['span']))[0]


def rex_compile(rex, flags=DEF_FLAGS):
    if isinstance(rex, REX_TYPE):
        return rex
    return re.compile(rex, flags=flags)


def rex_flex(rex, txt, fun=re.search, flags=DEF_FLAGS, pad=True):
    """

    :param rex:
    :param txt:
    :param fun:
    :param flags:
    :param pad:
    :return:

    """
    if pad:
        txt = ' ' + txt + ' '

    kwargs = {
        'pattern' : rex,
        'string' : txt,
    }
    if not isinstance(rex, REX_TYPE):
        kwargs['flags'] = flags

    return fun(**kwargs)


def rex_ctx(match=None, txt=None, ptn=None, flags=DEF_FLAGS, nchar=NCHAR,
            nchar_pre=None, nchar_post=None, pad=True):
    """

    :param match:
    :param txt:
    :param ptn:
    :param flags:
    :param nchar:
    :param nchar_pre:
    :param nchar_post:
    :return: If match found, tuple of context text and span; else None

    """
    nchar_pre = nchar_pre if nchar_pre is not None else nchar
    nchar_post = nchar_post if nchar_post is not None else nchar

    if match is None:
        match = rex_flex(ptn, txt, flags=flags)

    if match:
        span = match.span()
        start = max(0, span[0] - nchar_pre - 1)
        stop = min(span[1] + nchar_post - 1, len(txt))
        if pad:
            span = (
                max(0, span[0] - 1),
                span[1] - 1
            )
        return txt[start:stop], span


class Looks(object):

    def __init__(self, posbehind=None, negbehind=None, posahead=None,
                 negahead=None):
        self.posbehind = posbehind
        self.negbehind = negbehind
        self.posahead = posahead
        self.negahead = negahead

    def to_rex(self):

        behind, ahead = r'', r''
        if self.posbehind:
            behind += rex_posbehind(self.posbehind)
        if self.negbehind:
            behind += rex_negbehind(self.negbehind)
        if self.posahead:
            ahead += rex_posahead(self.posahead)
        if self.negahead:
            ahead += rex_negahead(self.negahead)

        return behind, ahead


class Tag(dict):
    """

    """

    def _no_context(self):

        return {
            key: value
            for key, value in self.iteritems()
            if key not in ['context', 'group', 'span']
        }

    def __eq__(self, other):

        return self._no_context() == other._no_context()

    def __repr__(self):

        dict_repr = super(Tag, self).__repr__()
        return 'Tag({})'.format(dict_repr)


class TagGroup(object):

    def __init__(self, taggers, category):
        self.taggers = taggers
        self.labels = [tagger.label for tagger in taggers]
        self.category = category

    @classmethod
    def from_module(cls, module):
        return cls(
            [
                var
                for var in module.__dict__.values()
                if hasattr(var, 'tag') and not isinstance(var, type)
            ],
            module.category
        )


class Tagger(object):

    def tag(self, txt):
        raise NotImplementedError


class CustomTagger(Tagger):

    def __init__(self, label, tag_func):
        self.label = label
        self.tag_func = tag_func

    def _as_tag(self, data):
        with_context = dict(data.items() + [('label', self.label)])
        return Tag(with_context)

    def tag(self, txt):
        rv = self.tag_func(txt)
        if isinstance(rv, list):
            return [self._as_tag(item) for item in rv]
        return self._as_tag(rv)


class RexTagger(Tagger):

    def __init__(self, label, rexes, compile_rex=True, flags=DEF_FLAGS,
                 nchar=NCHAR):
        self.label = label
        if compile_rex:
            rexes = [rex_compile(rex, flags=flags) for rex in rexes]
        self.rexes = rexes
        self.flags = flags
        self.nchar = nchar

    def tag(self, txt):
        tags = []
        for rex in self.rexes:
            match = rex_flex(rex, txt, flags=self.flags)
            if match:
                context, span = rex_ctx(match, txt, nchar=self.nchar)
                group = match.group()
                tags.append(Tag({
                    'label': self.label,
                    'context': context,
                    'group': group,
                    'span': span,
                }))
        if tags:
            return first_match(tags)


class RexVersionTagger(Tagger):

    def __init__(self, label, rexes, separator, looks=None, compile_rex=True,
                 flags=DEF_FLAGS, nchar=NCHAR):

        self.label = label
        self.rexes = rexes
        self.separator = separator
        self.looks = looks or Looks()
        self.compile_rex = compile_rex
        self.flags = flags
        self.nchar = nchar


class RexArbitraryVersionTagger(RexVersionTagger):

    def __init__(self, label, rexes, separator, looks, arbitrary_rex,
                 compile_rex=True, flags=DEF_FLAGS, nchar=NCHAR,
                 post_proc=None):

        super(RexArbitraryVersionTagger, self).__init__(
            label, rexes, separator, looks, compile_rex, flags, nchar
        )

        if '?P<version>' not in arbitrary_rex:
            raise Exception('Version rex must contain a group named "version".')
        self.arbitrary_rex = arbitrary_rex

        self.post_proc = post_proc

        self._build_taggers()

    def _build_taggers(self):
        """Build a list of regular expressions, each containing a group
        named "version"; store in self._taggers

        """
        behind, ahead = self.looks.to_rex()
        self._taggers = [
            rex + self.separator + behind + self.arbitrary_rex + ahead
            for rex in self.rexes
        ]
        if self.compile_rex:
            self._taggers = [
                re.compile(rex, self.flags)
                for rex in self._taggers
            ]

    def tag(self, txt):

        results = {}
        for rex in self._taggers:
            matches = rex_flex(rex, txt, re.finditer, flags=self.flags)
            for match in matches:
                version = match.groupdict()['version']
                if self.post_proc:
                    version = self.post_proc(version)
                if version not in results:
                    context, span = rex_ctx(match, txt, nchar=self.nchar)
                    group = match.group()
                    results[version] = (context, group, span)

        return [
            Tag({
                'label': self.label,
                'version': version,
                'context': context[0],
                'group': match.group(),
                'span': span[1],
            })
            for version, context in results.iteritems()
        ]


class RexKnownVersionTagger(RexVersionTagger):

    def __init__(self, label, rexes, separator, looks, versions,
                 compile_rex=True, flags=DEF_FLAGS, nchar=NCHAR):

        super(RexKnownVersionTagger, self).__init__(
            label, rexes, separator, looks, compile_rex, flags, nchar
        )

        if isinstance(versions, list):
            self.versions = {version : [version] for version in versions}
        elif isinstance(versions, dict):
            self.versions = {
                name : (rexes if isinstance(rexes, list) else [rexes])
                for name, rexes in versions.iteritems()
            }
        else:
            raise Exception('Versions must be a list or a dict.')

        self._build_taggers()

    def _build_taggers(self):
        behind, ahead = self.looks.to_rex()
        self._taggers = {}

        for name, version_rexes in self.versions.iteritems():
            self._taggers[name] = []
            if not isinstance(version_rexes, list):
                version_rexes = [version_rexes]
            for rex in self.rexes:
                for version_rex in version_rexes:
                    tagger = rex + self.separator + behind + version_rex + ahead
                    if self.compile_rex:
                        tagger = re.compile(tagger, self.flags)
                    self._taggers[name].append(tagger)

    def _tag_version(self, version, rexes, txt):

        tags = []
        for version_rex in rexes:
            match = rex_flex(version_rex, txt, flags=self.flags)
            if match:
                context, span = rex_ctx(match, txt, nchar=self.nchar)
                group = match.group()
                tags.append(Tag({
                    'label': self.label,
                    'version': version,
                    'context': context,
                    'group': group,
                    'span': span,
                }))
        if tags:
            return first_match(tags)

    def tag(self, txt):

        tags = []
        for name, version_rexes in self._taggers.iteritems():
            result = self._tag_version(name, version_rexes, txt)
            if result:
                tags.append(result)

        return tags


class RexComboVersionTagger(Tagger):

    def __init__(self, label, rexes, separator, looks=None, versions=None,
                 arbitrary_rex=None, compile_rex=True, flags=DEF_FLAGS,
                 nchar=NCHAR, post_proc=None):

        self.label = label

        self.boolean_tagger = RexTagger(label, rexes, flags=flags)
        self.known_version_tagger = (
            RexKnownVersionTagger(label, rexes, separator, looks, versions,
                                  compile_rex, flags, nchar)
            if versions
            else None
        )
        self.arbitrary_version_tagger = (
            RexArbitraryVersionTagger(label, rexes, separator, looks,
                                      arbitrary_rex, compile_rex, flags, nchar,
                                      post_proc=post_proc)
            if arbitrary_rex
            else None
        )

    def tag(self, txt):

        results = []

        # Check for tags with versions
        if self.known_version_tagger:
            uextend(results, self.known_version_tagger.tag(txt))
        if self.arbitrary_version_tagger:
            uextend(results, self.arbitrary_version_tagger.tag(txt))

        # If no versions found, check for tag without version, labeling
        # version as unknown if found
        if not results:
            boolean_result = self.boolean_tagger.tag(txt)
            if boolean_result:
                boolean_result['version'] = UNKNOWN_VERSION
                results = [boolean_result]

        return results


class MultiRexTagger(Tagger):

    def __init__(self, label, rexes_primary, rexes_secondary=None,
                 rexes_negative=None, separator=None, compile_rex=False,
                 flags=DEF_FLAGS, nchar=NCHAR):

        self.label = label
        self.separator = separator or ''
        self.flags = flags
        self.nchar = nchar

        if compile_rex:
            rexes_primary = [rex_compile(rex, flags=flags) for rex in rexes_primary]
            rexes_secondary = [rex_compile(rex, flags=flags) for rex in (rexes_secondary or [])]
            rexes_negative = [rex_compile(rex, flags=flags) for rex in (rexes_negative or [])]

        self.rexes_primary = rexes_primary
        self.rexes_secondary = rexes_secondary or []
        self.rexes_negative = rexes_negative or []

    def _any_match(self, rexes, context):
        for rex in rexes:
            if rex_flex(rex, context, flags=self.flags):
                return True
        return False

    def _secondary_match(self, rex, context, span):
        tags = []
        for secondary in self.rexes_secondary:
            if self.separator:
                context_patterns = [
                    rex + self.separator + secondary,
                    secondary + self.separator + rex,
                ]
            else:
                context_patterns = [secondary]
            for pattern in context_patterns:
                match = rex_flex(pattern, context, flags=self.flags)
                if match:
                    group = match.group()
                    tags.append(Tag({
                        'label': self.label,
                        'context': context,
                        'group': group,
                        'span': span,
                    }))
        return tags

    def tag(self, txt):
        tags = []
        for rex in self.rexes_primary:
            for match in rex_flex(rex, txt, fun=re.finditer, flags=self.flags):
                context, span = rex_ctx(match, txt, nchar=self.nchar)
                if self._any_match(self.rexes_negative, context):
                    continue
                if self.rexes_secondary:
                    tags.extend(self._secondary_match(rex, context, span))
                else:
                    group = match.group()
                    tags.append(Tag({
                        'label': self.label,
                        'context': context,
                        'group': group,
                        'span': span,
                    }))
        if tags:
            return first_match(tags)


def tag(tag_group, txt):
    """Extract tags from text.

    :param tag_group: TagGroup object
    :param txt: Text to be tagged
    :return: List of Tag objects

    """
    results = []

    for tagger in tag_group.taggers:

        tags = tagger.tag(txt)

        if tags is None:
            continue

        if not isinstance(tags, list):
            tags = [tags]
        if isinstance(tags, list):
            uextend(results, tags)

    for tag in results:
        tag['category'] = tag_group.category

    return results
