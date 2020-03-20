from setuptools import setup, find_packages

setup(
    name='cloudburst',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A python package for targeted data dumps',
    long_description=open('README.md').read(),
    install_requires=[''],
    url='https://github.com/concurrent-studio/cloudburst',
    author='CONCURRENT STUDIO™',
    author_email='info@concurrent.studio'
)
