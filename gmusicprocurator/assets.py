# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Mark Lee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""webassets-related code for GMusicProcurator."""

from flask.ext.assets import Bundle
try:
    import sass
except ImportError:
    sass_filter = 'scss'
else:
    import os.path
    from webassets.filter import Filter
    sass_filter = 'libsass'
from webassets.filter import ExternalTool, register_filter

from .app import assets

if sass_filter == 'libsass':

    class LibSassFilter(Filter):

        """webassets Filter for libsass-python."""

        name = 'libsass'

        def input(self, _in, out, **kw):
            """
            Based on the pyscss filter.

            Makes sure that the ``include_paths`` parameter includes the
            directory of the source file.
            """
            source_path = kw['source_path']
            include_paths = [os.path.dirname(source_path)]
            out.write(sass.compile(string=_in.read(),
                                   include_paths=include_paths))

    register_filter(LibSassFilter)


class ImporterFilter(ExternalTool):

    """
    webassets_ filter for Importer_.

    .. _webassets: https://webassets.readthedocs.org/
    .. _Importer: https://github.com/devongovett/importer
    """

    name = 'importer_js'
    method = 'open'
    options = {
        'binary': 'IMPORTERJS_BIN',
        'extra_args': 'IMPORTERJS_EXTRA_ARGS',
    }

    def setup(self):
        """Set up Importer CLI args."""
        self.argv = [
            self.binary or 'importer',
            '{1}',  # source_path
            '{{output}}',
        ]
        if self.extra_args:
            self.argv.extend(self.extra_args)

register_filter(ImporterFilter)


def bundlify(fmt, modules, **kwargs):
    """Create a Bundle based on a path format and a list of modules."""
    return Bundle(*[fmt.format(f) for f in modules], **kwargs)

normalize = 'vendor/normalize-css/normalize.css'

# typography is in a separate bundle so it can be placed before pure
typography = Bundle('scss/typography.scss', filters=sass_filter,
                    output='scss/typography.out.css')

pure_modules = [
    'buttons',
    'tables',
]

pure = bundlify('vendor/pure/{0}.css', pure_modules)

main_css = Bundle('scss/main.scss', filters=sass_filter,
                  output='scss/main.out.css')

css = Bundle(normalize, typography, pure, main_css, filters='cssmin',
             output='all.min.css')
assets.register('css', css)

aurora = Bundle('vendor/aurora.js/browser_slim.coffee', filters='importer_js',
                output='vendor/aurora.built.js')
mp3 = Bundle('vendor/mp3.js/mp3.js', filters='importer_js',
             output='vendor/mp3.built.js')
aurora_mp3 = Bundle(aurora, mp3, filters='uglifyjs', output='auroramp3.min.js')
assets.register('aurora_mp3', aurora_mp3)

vendor_js = [
    'vendor/jquery/dist/jquery.js',
    'vendor/lodash/dist/lodash.js',
    'vendor/backbone/backbone.js',
    'vendor/backbone.localstorage/backbone.localStorage.js',
    'vendor/html5-desktop-notifications/desktop-notify.js',
]

vendor = Bundle(*vendor_js)

cs_modules = [
    'init',
    'backends/webaudio',
    'backends/aurora',
    'player',
    'playlist',
    'queue',
    'app',
]

cs = bundlify('cs/{0}.coffee', cs_modules, filters='coffeescript',
              output='cs/out.js')
js = Bundle(vendor, cs, filters='uglifyjs', output='all.min.js')
assets.register('js', js)
