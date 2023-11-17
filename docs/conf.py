# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Keltner-Channels"
copyright = "2023, Giovanni Sanchez"
author = "Giovanni Sanchez"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
extensions = [
    "sphinx.ext.autodoc",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

import os
import sys

# Aggiungi il percorso dei moduli da documentare al path di sistema
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("../src/btToolbox"))

autodoc_mock_imports = ["config"]

# Abilita l'estensione autodoc di Sphinx
extensions = [
    "sphinx.ext.autodoc",
    # Altre estensioni...
]

# Specifica i moduli da documentare
autodoc_member_order = "bysource"

autodoc_files = [
    "backtestingMainKC",
    "liveMainKC",
    "parseArgs",
    "btToolbox.backtestingAnalysis",
    "btToolbox.backtestingRetrivesDatas",
    "btToolbox.indicatorKC",
    "btToolbox.loggingUtils",
    "btToolbox.retrievesDataBroker",
    "btToolbox.strategyKC",
]
