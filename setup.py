from setuptools import setup, find_packages

setup(
    name="cloudburst",
    version="0.1.2",
    packages=find_packages(exclude=['tests*']),
    license="MIT",
    description="A python package for computational design by CONCURRENT STUDIO\u2122",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[],
    url="https://github.com/concurrent-studio/cloudburst",
    author="concurrent-studio",
    author_email="info@concurrent.studio",
    package_data={
        'cloudburst': ['cloudburst/vision/models/*.xml']
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research"
    ]
)
