#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['wtforms', 'pydantic[email]']
test_requires = ['pytest>=3', 'PyHamcrest']

setup(
    author="Christian Klinger",
    author_email='ck@novareto.de',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="WTForms out of Pydantic",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='wtforms_pydantic',
    name='wtforms_pydantic',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extras_require={
        'test': test_requires,
    },
    url='https://github.com/goschtl/wtforms_pydantic',
    version='0.1.0',
    zip_safe=False,
)
