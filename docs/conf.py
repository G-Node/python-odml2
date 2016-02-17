# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from odml2.info import RELEASE, COPYRIGHT, DESCRIPTION

# general config
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
source_suffix = '.rst'
master_doc = 'index'
project = DESCRIPTION
copyright = COPYRIGHT
release = RELEASE
exclude_patterns = []
pygments_style = 'sphinx'

# html options
htmlhelp_basename = 'odml2'
try:
    import alabaster

    html_theme_path = [alabaster.get_path()]
    html_static_path = ['_static']
    extensions += ['alabaster']
    html_theme = 'alabaster'

    html_sidebars = {
        '**': ['about.html', 'navigation.html', 'searchbox.html']
    }

    html_theme_options = {
        'logo': 'logo.png',
        'github_user': 'G-Node',
        'github_repo': 'python-odml2',
        'github_button': True,
        'github_count': False,
        #'travis_button': True,
        'link': '#456BA8'
    }

except ImportError:
    html_theme = 'default'

# intersphinx configuration
intersphinx_mapping = {
    'http://docs.python.org/2.7': None
}
