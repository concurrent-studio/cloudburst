import yaml
from setuptools import setup, find_packages

pypak = yaml.load(open("pypak.yml"), Loader=yaml.FullLoader)

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8"
]

def dev_status(ds):
    if ds:
        if ds == "planning":
            classifiers.append("Development Status :: 1 - Planning")
        elif ds == "pre alpha":
            classifiers.append("Development Status :: 2 - Pre-Alpha")
        elif ds == "alpha":
            classifiers.append("Development Status :: 3 - Alpha")
        elif ds == "beta":
            classifiers.append("Development Status :: 4 - Beta")
        elif ds == "production/stable":
            classifiers.append("Development Status :: 5 - Production/Stable")
        elif ds == "mature":
            classifiers.append("Development Status :: 6 - Mature")
        elif ds == "inactive":
            classifiers.append("Development Status :: 7 - Inactive")
        else:
            print("Error: improper intended audience given")
            print("Please choose from [planning, pre alpha, alpha, beta, production/stable, mature, inactive]")
            raise
    else:
        pass

def intended_audience(ia):
    if ia:
        if ia == "customer service":
            classifiers.append("Intended Audience :: Customer Service")
        elif ia == "developers":
            classifiers.append("Intended Audience :: Developers")
        elif ia == "education":
            classifiers.append("Intended Audience :: Education")
        elif ia == "end users/desktop":
            classifiers.append("Intended Audience :: End Users/Desktop")
        elif ia == "financial/insurance":
            classifiers.append("Intended Audience :: Financial and Insurance Industry")
        elif ia == "healthcare":
            classifiers.append("Intended Audience :: Healthcare Industry")
        elif ia == "it":
            classifiers.append("Intended Audience :: Information Technology")
        elif ia == "legal":
            classifiers.append("Intended Audience :: Legal Industry")
        elif ia == "manufacturing":
            classifiers.append("Intended Audience :: Manufacturing")
        elif ia == "other":
            classifiers.append("Intended Audience :: Other Audience")
        elif ia == "religion":
            classifiers.append("Intended Audience :: Religion")
        elif ia == "science/research":
            classifiers.append("Intended Audience :: Science/Research")
        elif ia == "sysadmin":
            classifiers.append("Intended Audience :: System Administrators")
        elif ia == "telecomm":
            classifiers.append("Intended Audience :: Telecommunications Industry")
        else:
            print("Error: improper intended audience given")
            print("Please choose from [customer service, developers, education, end users/desktop. financial/insurance, healthcare, it, legal, manufacturing, other, religion, science/research, sysadmin, telecomm]")
            raise
    else:
        pass

dev_status(pypak["classifiers"]["dev status"])
intended_audience(pypak["classifiers"]["intended audience"])

setup(
    name=pypak["name"],
    version=pypak["version"],
    packages=find_packages(exclude=['tests*']),
    license=pypak["license"],
    description=pypak["description"],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=["twine", "black"],
    url=pypak["git url"],
    author=pypak["author"],
    author_email=pypak["author email"],
    package_data={
        'cloudburst': ['cloudburst/vision/models/*.xml']
    },
    classifiers=classifiers
)
