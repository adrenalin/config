"""
Configuration class

@author Arttu Manninen <arttu@kaktus.cc>
"""
import setuptools

description = 'Multi tier configuration utility that leverages YAML, \
AWS Secrets Manager and environment variables with tree structures'

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='config',
    version='0.0.1',
    author='Arttu Manninen',
    author_email='arttu@kaktus.cc',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adrenalin/config',
    packages=setuptools.find_packages(
        '.',
        exclude=[
            'tests',
            'tests.*'
        ]
    ),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6'
)
