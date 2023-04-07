"""
This module is a directory of internal plugins.
"""

from breadcrumbs.display_plugin import load_plugin as display
from breadcrumbs.core_plugin import load_plugin as core
from breadcrumbs.future_plugin import load_plugin as future
from breadcrumbs.metrics_plugin import load_plugin as metrics
from breadcrumbs.default_macros_plugin import load_plugin as default_macros

# The directory
directory = {
    'display': display,
    'core': core,
    'future': future,
    'metrics': metrics,
    'default_macros': default_macros
}

