from setuptools import setup, find_packages

setup(name="cloudburst",
      version="0.1.4",
      packages=find_packages(exclude=['tests*']),
      license="Apache 2.0",
      description="Quickly grab lots of data",
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      install_requires=find_packages(),
      url="https://github.com/concurrent-studio/cloudburst",
      author="concurrent-studio",
      author_email="info@concurrent.studio",
      package_data={},
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
      ])
