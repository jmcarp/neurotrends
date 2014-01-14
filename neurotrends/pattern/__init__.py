import des, lang, mag, mcc, mod, opsys, pkg, proc, pulse, spc, stat, task, tbx, tech
from neurotrends.tagger import TagGroup
from types import ModuleType

tag_groups = {
    key: TagGroup.from_module(value)
    for key, value in locals().items()
    if isinstance(value, ModuleType)
        and hasattr(value, 'category')
}
