from distutils.core import setup

setup(name='money',
        version='1.0',
        packages=['money',
                  'money.contrib',
                  'money.contrib.django',
                  'money.contrib.django.forms',
                  'money.contrib.django.models']
)
