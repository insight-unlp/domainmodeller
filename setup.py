from setuptools import setup, find_packages
import sys, os

install_requires = [
    'gevent',
    'sqlalchemy',
    'celery==3.0.24', # 3.1.5 is latest at time of writing and is slow for some reason
    'requests',
    'pattern',
    'oursql',
    'grequests',
    'nltk',
    'luigi',
    'snakebite',
    'termcolor',
    'functools32', # Backport of Python 3 functools
]


setup(
    name = "domainmodeller",
    version = "1.1", 
    packages = find_packages(),

    install_requires = install_requires,

    tests_require=[
        'nose',
        'coverage',
        'HTTPretty'
    ],
    
    dependency_links = ['https://github.com/clips/pattern/archive/2.6.tar.gz#egg=pattern'],

    entry_points = {
        'console_scripts': [
            'domainmodeller = domainmodeller.main:main',
        ]
    },
)

# Need to call an external script because distribute will 
# not update the python path after installation
if 'install' in sys.argv or 'develop' in sys.argv:
    os.system("python setup_postinstall.py")
