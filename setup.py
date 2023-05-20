from setuptools import setup, find_packages

__version__ = "1.0.0-alpha"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='Wakaba64',
    version=__version__,
    description='4chan-like Fediverse explorer',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'Django',
        'Mastodon.py'
    ],
    url='https://github.com/web3chan/Wakaba64',
    author='zhoreeq',
    author_email='zhoreeq@protonmail.com',
    keywords='web3 Fediverse 4chan Mastodon',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
    ]
)
