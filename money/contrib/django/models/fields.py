from django.db import models
from django.utils.encoding import smart_unicode
from money.contrib.django import forms
from money import Money
from decimal import Decimal
import re

__all__ = ('MoneyField', 'NotSupportedLookup')

#currency_field_name = lambda name: "(%s).currency" % name

SUPPORTED_LOOKUPS = ('exact', 'lt', 'gt', 'lte', 'gte')

class NotSupportedLookup(Exception):
    def __init__(self, lookup):
        self.lookup = lookup
    def __str__(self):
        return "Lookup '%s' is not supported for MoneyField" % self.lookup

class MoneyFieldProxy(object):
    def __init__(self, field):
        self.field = field
#        self.currency_field_name = currency_field_name(self.field.name)
    
    def _money_from_obj(self, obj):
        return Money(obj.__dict__[self.field.name], obj.__dict__[self.currency_field_name])
    
    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        if not isinstance(obj.__dict__[self.field.name], Money):
            obj.__dict__[self.field.name] = self._money_from_obj(obj)
        return obj.__dict__[self.field.name]
    
    def __set__(self, obj, value):
        if isinstance(value, Money):
            obj.__dict__[self.field.name] = value.amount  
            setattr(obj, self.currency_field_name, smart_unicode(value.currency))
        else:
            if value: value = str(value)
            obj.__dict__[self.field.name] = self.field.to_python(value) 


class MoneyField(models.Field):
    description = 'Money field'
    __metaclass__ = models.SubfieldBase
    def __init__(self, verbose_name=None, name=None,
                 max_digits=None, decimal_places=None,
                 default=None, default_currency=None, **kwargs):
        if isinstance(default, Money):
            self.default_currency = default.currency
        self.default_currency = default_currency
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        super(MoneyField, self).__init__(verbose_name, name, default=default, **kwargs)

    def get_internal_type(self):
         return "DecimalField"

    def db_type(self, _connection):
        return 'u_money'

    postgres_money_re = re.compile('\((\d+\.\d{2}),([A-Z]{3})\)')
    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, Money):
            return value
        elif isinstance(value, Decimal):
            return Money(value)
        else:
            m = self.postgres_money_re.match(value)
            if m is not None:
                return Money(amount=m.group(1), currency=m.group(2))
            else:
                return Money.from_string(value)

#    def contribute_to_class(self, cls, name):
#        c_field_name = currency_field_name(name)
#        c_field = models.CharField(max_length=3, default=self.default_currency, editable=False)
#        c_field.creation_counter = self.creation_counter
#        cls.add_to_class(c_field_name, c_field)

#        super(MoneyField, self).contribute_to_class(cls, name)

#        setattr(cls, self.name, MoneyFieldProxy(self))

#        if not hasattr(cls, '_default_manager'):
#            from managers import MoneyManager
#            cls.add_to_class('objects', MoneyManager())

    def get_db_prep_save(self, value):
        return value.amount, str(value.currency)

#    def get_db_prep_lookup(self, lookup_type, value):
#        if not lookup_type in SUPPORTED_LOOKUPS: 
#            raise NotSupportedLookup(lookup_type)
#        value = self.get_db_prep_save(value)
#        return super(MoneyField, self).get_db_prep_lookup(lookup_type, value)

    def get_default(self):
        if isinstance(self.default, Money):
            return self.default
        else:
            return super(MoneyField, self).get_default()

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.MoneyField}
        defaults.update(kwargs)
        return super(MoneyField, self).formfield(**defaults)
