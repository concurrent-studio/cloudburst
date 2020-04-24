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
# import sphinx_bootstrap_theme

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
]

autosummary_generate = True
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "bootstrap"
# html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
# html_theme_options = {
#     # Navigation bar title. (Default: ``project`` value)
#     "navbar_title": "cloudburst ⛈",
#     "navbar_site_name": "Page",
#     # A list of tuples containing pages or urls to link to.
#     # Valid tuples should be in the following forms:
#     #    (name, page)                 # a link to a page
#     #    (name, "/aa/bb", 1)          # a link to an arbitrary relative url
#     #    (name, "http://example.com", True) # arbitrary absolute url
#     # Note the "1" or "True" value above as the third argument to indicate
#     # an arbitrary url.
#     "navbar_links": [("CONCURRENT™", "http://www.concurrent.studio", True),],
#     # Tab name for the current pages TOC. (Default: "Page")
#     "navbar_pagenav_name": "Heading",
#     "navbar_class": "navbar navbar-inverse",
#     # Fix navigation bar to top of page?
#     # Values: "true" (default) or "false"
#     "navbar_fixed_top": "true",
#     # Location of link to source.
#     # Options are "nav" (default), "footer" or anything else to exclude.
#     "source_link_position": "nav",
#     # Bootswatch (http://bootswatch.com/) theme.
#     # Currently, the supported themes are:
#     # - Bootstrap 2: https://bootswatch.com/2
#     # - Bootstrap 3: https://bootswatch.com/3
#     "bootswatch_theme": "yeti",
#     # Choose Bootstrap version.
#     # Values: "3" (default) or "2" (in quotes)
#     "bootstrap_version": "3",
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

# html_extra_path = ["_static/OfficeCodeProD-Regular.woff"]
# html_static_path = ["_static"]


# def setup(app):
#     app.add_stylesheet("concurrent.css")
