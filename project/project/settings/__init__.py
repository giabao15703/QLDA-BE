"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings
https://sobolevn.me/2017/04/managing-djangos-settings

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

import os
from split_settings.tools import include, optional

# Managing environment via `DJANGO_ENV` variable:
os.environ.setdefault('DJANGO_ENV', 'dev')
ENV = os.environ['DJANGO_ENV']

base_settings = (
    'components/common.py',

    # Select the right env:
    'environments/{0}.py'.format(ENV),

    # Optionally override some settings:
    optional('environments/local.py'),
)

# Include settings:
include(*base_settings)