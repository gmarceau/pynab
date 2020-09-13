from pprint import pprint
from jsobject import Object
from forbiddenfruit import curse
from json_objects import Object_recursive # type: ignore
from weakref import WeakValueDictionary

shells = WeakValueDictionary()

spells = set()

def new_or_cached_shell(v):
    global shells
    if id(v) in shells:
        return shells[id(v)]

    result = Shell(v)
    shells[id(v)] = result
    return result

@property
def jsobject_up(self):
    """Detects all the spells that have methods for this object. Returns a shells that
    proxy to this object, and decorates it with the compatible methods.

    Shells are cached according to `id` so that multiple calls to `up` return
    the same shell.

    If you no longer need a shell and want to reclaim memory prior to the object being
    garbage collected, call `down()`
    """
    result = new_or_cached_shell(self)
    result._detect()
    return result

setattr(Object, 'up', jsobject_up)
curse(list, 'up', jsobject_up)

def find_beam(v, active_spells, destination_spell_name):
    result = []
    destination_spell_name += 'Spell'
    for s in active_spells:
        for attribute_name, attr in s.__dict__.items():
            beams_to = getattr(attr, 'beams_to', None)
            if beams_to and beams_to.__name__.lower() == destination_spell_name.lower():
                result.append(attr)

    if not result:
        raise Exception('could not find beam to {} for {}'.format(destination_spell_name, v))
    if len(result) > 1:
        raise Exception('found more than one beam to {}: {}'.format(destination_spell_name, result))
    return result[0]

def find_beam_to(active_spells, destination_spell):
    pass

def beam_to(destination_spell):
    def tagger(func):
        setattr(func, 'beams_to', destination_spell)
        return func
    return tagger

class Shell:
    """Proxy to the original value `v`, while decorating it with all the methods
    from the compatible spells.

    Compatibility is check by scanning through all spells in the global `spells`
    list and called `_detect` on each one.
    """
    def __init__(self, v):
        self.__dict__['_v'] = v
        self.__dict__['_active_spells']= set()

    def _detect(self):
        global spells
        self.__dict__['_active_spells'] = {s for s in spells if s._detect(self._v)}
        print('--74', spells)
        print('--75', self.__dict__['_active_spells'])

    def __getattr__(self, name):
        print('--34 getattr', name, self.__dict__['_active_spells'])

        for c in self.__dict__['_active_spells']:
            method = getattr(c, name, None)
            if method:
                return method.__get__(self.__dict__['_v'], c)

        return getattr(self.__dict__['_v'], name)

    def __setattr__(self, name, vv):
        return setattr(self._v, name, vv)

    def __getitem__(self, i):
        return self.__dict__['_v'][i]

    def __len__(self):
        return len(self.__dict__['_v'])

    def __str__(self):
        return str(self.__dict__['_v'])

    @property
    def to(self):
        print('--99', self.__dict__['_active_spells'])

        class To:
            def __getattr__(sub_self, destination_spell_name):
                beam = find_beam(self, self.__dict__['_active_spells'], destination_spell_name)
                destination_spell = getattr(beam, 'beams_to')
                def wrapper(*args, **xargs):
                    result = beam(self, *args, **xargs)
                    print('--109', result, type(result), destination_spell)
                    assert(destination_spell._detect(result))
                    result = new_or_cached_shell(result)
                    result.__dict__['_active_spells'].add(destination_spell)
                    return result
                return wrapper

        return To()



    def beam_to(self, destination_spell):
        beam = find_beam_to(self.__dict__['_active_spells'], destination_spell)
        if not beam:
            raise Exception('could not find beam to {} for {}'.format(destination_spell, self))
        return beam(self)
        # TODO

    def down(self):
        if id(self.__dict__['_v']) in shells:
            del shells[id(self.__dict__['_v'])]
        return self.__dict__['_v']

class Spell:
    @classmethod
    def study_globally(cls):
        global spells
        spells.add(cls)
