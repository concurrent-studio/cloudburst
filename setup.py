from setuptools import setup, find_packages

setup(
    name='cloudburst',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A python package for computational design by CONCURRENT STUDIO™',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[''],
    url='https://github.com/concurrent-studio/cloudburst',
    author='CONCURRENT STUDIO™',
    author_email='info@concurrent.studio',
    license="CC-BY-NC-SA-4.0",
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
