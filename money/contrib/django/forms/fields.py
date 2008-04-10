from django import newforms as forms
from widgets import InputMoneyWidget
from money import Money

__all__ = ('MoneyField',)

class MoneyField(forms.DecimalField):
    widget = InputMoneyWidget()
    
    def clean(self, value):
        #TODO: check that value is tupple
        amount = super(MoneyField, self).clean(value[0])
        currency = value[1]#TODO: check - is currency valid
        return Money(amount=amount, currency=currency)