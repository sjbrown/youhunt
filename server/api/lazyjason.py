# api.lazyjason

import json


class LazyJason(object):
    _lazy_defaults = {}

    def load(self):
        self._orig_db_attrs = self.db_attrs
        if hasattr(self, '_jdict'):
            return
        #print 'trying to load', self.db_attrs
        try:
            self._jdict = json.loads(self.db_attrs)
        except ValueError:
            print 'Corrupt db_attrs'
        for key, val in self._lazy_defaults.items():
            if key not in self._jdict:
                self._jdict[key] = val

    def freeze_db_attrs(self):
        if self.db_attrs != self._orig_db_attrs:
            # Someone has gone in raw and changed db_attrs.  It was probably
            # the Django admin interface.
            # Or else it was multiple calls to save()
            print '--'
            print 'Lost track of the source of truth on ', self
            print '--'
            try:
                self._jdict = json.loads(self.db_attrs)
                print 'db_attrs clobbers _jdict'
            except ValueError:
                print 'db_attrs invalid, _jdict clobbers db_attrs'

        if self.db_attrs == '{}':
            # Brand new in the original packaging
            dba = self._lazy_defaults.copy()
        else:
            # We may have added some items to _lazy_defaults since last save
            dba = json.loads(self.db_attrs)
            print 'non default dba', dba
            for key,val in self._lazy_defaults.items():
                if key not in dba:
                    print 'key %s was not in dba' % key
                    dba[key] = val
        if hasattr(self, '_jdict'):
            dba.update(self._jdict)
        else:
            print 'SHOULD NOT GET HERE'

        self.db_attrs = json.dumps(dba)

    def __getattr__(self, attrname):
        #if not hasattr(self, '_jdict'):
        #    print 'LasyJason needs to load() first'
        if attrname in self._jdict:
            return self._jdict[attrname]
        if attrname.endswith('__object'):
            return self.lookup_object_by_id(attrname, self._jdict)
        if attrname.endswith('__objects'):
            return self.lookup_objects_by_id(attrname, self._jdict)
        return object.__getattribute__(self, attrname)

    def lazy_set(self, **kwargs):
        self._jdict.update(kwargs)

    def __setattr__(self, attrname, val):
        if hasattr(self, '_jdict') and attrname in self._jdict:
            if isinstance(val, LazyJason):
                print 'jdict values should be stringed ids of model objects'
                val = str(val.id)
            if isinstance(val, list) and val and isinstance(val[0], LazyJason):
                print 'jdict values should be stringed ids of model objects'
                val = [str(x.id) for x in val]
            print 'a:v', {attrname:val}
            return self.lazy_set(**{attrname:val})
        return super(LazyJason, self).__setattr__(attrname, val)

    def lookup_objects_by_id(self, attrname, lookup_dict):
        orig_attr_name, clsname, _, _ = attrname.rsplit('_',3)
        objids = lookup_dict[orig_attr_name]
        obj_set = getattr(self.game, clsname.lower() + '_set')
        return obj_set.filter(id__in=objids)

    def lookup_object_by_id(self, attrname, lookup_dict):
        orig_attr_name, clsname, _, _ = attrname.rsplit('_',3)
        objid = lookup_dict[orig_attr_name]
        obj_set = getattr(self.game, clsname.lower() + '_set')
        return obj_set.get(id=objid)


    def to_dict(self, *extra_args):
        self.freeze_db_attrs()
        d = self._jdict.copy()
        d.update(id=self.id)
        for key in extra_args:
            d[key] = getattr(self, key)
        return d

def pre_save_for_lazies(**kwargs):
    instance = kwargs.get('instance')
    print 'in pre save for ', kwargs
    instance.freeze_db_attrs()

def post_init_for_lazies(**kwargs):
    instance = kwargs.get('instance')
    instance.load()
