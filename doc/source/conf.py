# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import importlib.metadata
import packaging

project = 'tinysoundfont'
copyright = '2024, Nathan Whitehead'
author = 'Nathan Whitehead'

# The short X.Y version
project_version = importlib.metadata.version(project)
release = project_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
    'sphinx_autodoc_typehints',
    'sphinx_tabs.tabs',
]
sphinx_tabs_disable_tab_closing = True
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
