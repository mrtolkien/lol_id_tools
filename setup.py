from distutils.core import setup
import setuptools  # noqa
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lol_id_tools',
    version='0.1.4',
    packages=['lol_id_tools'],
    url='https://github.com/mrtolkien/lol_id_tools',
    license='MIT',
    author='Tolki',
    install_requires=['requests',
                      'joblib',
                      'fuzzywuzzy[speedup]'],
    author_email='gary.mialaret+pypi@gmail.com',
    description='A tool to work with League of Legends-related object IDs.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)