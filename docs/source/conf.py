# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath("../../cloudburst"))


# -- Project information -----------------------------------------------------

project = "cloudburst"
copyright = "2020, CONCURRENT STUDIO™"
author = "CONCURRENT STUDIO™"

# The full version, including alpha/beta/rc tags
release = "0.1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # Allows sphinx-apidoc to work
    "sphinx.ext.todo",  # optional.  Allows inline "todo:"
    "sphinx.ext.imgmath",  # optional. Allows LaTeX equations
    "sphinx.ext.napoleon",  # Allows google/numpy docstrings
    "sphinx.ext.githubpages",  # Adds .nojekyll file
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "numpydoc",
    "sphinx_rtd_theme"
]

autosummary_generate = True
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
