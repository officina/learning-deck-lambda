from setuptools import setup

setup(
    name='gamecontroller',
    version='0.1',
    description='Gamecontroller',
    url='http://github.com/officina/mygenerali-lambda',
    author='Officine + Alessandro Dentella',
    author_email='adentella@thux.it',
    packages=['gamecontroller'],
    install_requires=[
        'setuptools',
        #'asn1crypto==0.24.0',
        'boto3==1.8.3',
        #'botocore==1.10.30',
        #'cffi==1.11.5',
        #'cryptography==1.9',
        #'docutils==0.14',
        #'idna==2.6',
        #'jmespath==0.9.3',
        #'jwt==0.5.3',
        'Playoff==0.7.1',
        #'pycparser==2.18',
        #'python-dateutil==2.7.3',
        #'s3transfer==0.1.13',
        #'six==1.11.0',
        'pynamodb==3.3.0',
        'pytz',
        'simplejson',
        'jsonschema==2.6.0'


    ],
    zip_safe=False,
    test_suite='tests.game_suite'
)
