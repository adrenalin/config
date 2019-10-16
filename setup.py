"""
Configuration class

@author Arttu Manninen <arttu@kaktus.cc>
"""
import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='config',
    version='0.0.1',
    author='Arttu Manninen',
    author_email='arttu@kaktus.cc',
    description='Configuration utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adrenalin/config',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
