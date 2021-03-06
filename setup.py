#!/usr/bin/env python

import sys, os, glob
from shutil import rmtree
from collections import defaultdict
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup_args = {}
install_requires = ['param>=1.5.1,<2.0', 'numpy>=1.0']
extras_require={}

# Notebook dependencies of IPython 3
extras_require['notebook-dependencies'] = ['ipython', 'pyzmq', 'jinja2', 'tornado',
                                           'jsonschema',  'notebook', 'pygments']
# IPython Notebook + matplotlib + Lancet
extras_require['recommended'] = (extras_require['notebook-dependencies']
                                 + ['matplotlib', 'lancet-ioam'])
# Additional, useful third-party packages
extras_require['extras'] = (['pandas', 'seaborn', 'bokeh>=0.12.6']
                            + extras_require['recommended'])
# Everything including cyordereddict (optimization) and nosetests
extras_require['all'] = (extras_require['recommended']
                         + extras_require['extras']
                         + ['cyordereddict', 'nose'])

setup_args.update(dict(
    name='holoviews',
    version="1.8.1",
    install_requires = install_requires,
    extras_require = extras_require,
    description='Stop plotting your data - annotate your data and let it visualize itself.',
    long_description=open('README.rst').read() if os.path.isfile('README.rst') else 'Consult README.rst',
    author= "Jean-Luc Stevens and Philipp Rudiger",
    author_email= "holoviews@gmail.com",
    maintainer= "IOAM",
    maintainer_email= "holoviews@gmail.com",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='http://www.holoviews.org',
    entry_points={
          'console_scripts': [
              'holoviews = holoviews.util.command:main'
          ]},
    packages = ["holoviews",
                "holoviews.core",
                "holoviews.core.data",
                "holoviews.element",
                "holoviews.interface",
                "holoviews.ipython",
                "holoviews.util",
                "holoviews.operation",
                "holoviews.plotting",
                "holoviews.plotting.mpl",
                "holoviews.plotting.bokeh",
                "holoviews.plotting.plotly",
                "holoviews.plotting.widgets"],
    package_data={'holoviews.ipython': ['*.html'],
                  'holoviews.plotting.mpl': ['*.mplstyle', '*.jinja', '*.js'],
                  'holoviews.plotting.bokeh': ['*.js', '*.css'],
                  'holoviews.plotting.plotly': ['*.js'],
                  'holoviews.plotting.widgets': ['*.jinja', '*.js', '*.css']},
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"]
))

def check_pseudo_package(path):
    """
    Verifies that a fake subpackage path for assets (notebooks, svgs,
    pngs etc) both exists and is populated with files.
    """
    if not os.path.isdir(path):
        raise Exception("Please make sure pseudo-package %s exists." % path)
    else:
        assets = os.listdir(path)
        if len(assets) == 0:
            raise Exception("Please make sure pseudo-package %s is populated." % path)


excludes = ['DS_Store', '.log', 'ipynb_checkpoints']
packages = []
extensions = defaultdict(list)

def walker(top, names):
    """
    Walks a directory and records all packages and file extensions.
    """
    global packages, extensions
    if any(exc in top for exc in excludes):
        return
    package = top[top.rfind('holoviews'):].replace(os.path.sep, '.')
    packages.append(package)
    for name in names:
        ext = '.'.join(name.split('.')[1:])
        ext_str = '*.%s' % ext
        if ext and ext not in excludes and ext_str not in extensions[package]:
            extensions[package].append(ext_str)


def package_assets(example_path):
    """
    Generates pseudo-packages for the examples directory.
    """
    import holoviews
    holoviews.util.examples(example_path, force=True, root=__file__)
    for root, dirs, files in os.walk(example_path):
        walker(root, dirs+files)
    setup_args['packages'] += packages
    for p, exts in extensions.items():
        if exts:
            setup_args['package_data'][p] = exts


if __name__=="__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'holoviews/examples')
    if not 'develop' in sys.argv:
        package_assets(example_path)

    if ('upload' in sys.argv) or ('sdist' in sys.argv):
        import holoviews
        holoviews.__version__.verify(setup_args['version'])

    if 'install' in sys.argv:
        header = "HOLOVIEWS INSTALLATION INFORMATION"
        bars = "="*len(header)

        extras = '\n'.join('holoviews[%s]' % e for e in setup_args['extras_require'])

        print("%s\n%s\n%s" % (bars, header, bars))

        print("\nHoloViews supports the following installation types:\n")
        print("%s\n" % extras)
        print("Users should consider using one of these options.\n")
        print("By default only a core installation is performed and ")
        print("only the minimal set of dependencies are fetched.\n\n")
        print("For more information please visit http://holoviews.org/install.html\n")
        print(bars+'\n')

    setup(**setup_args)

    if os.path.isdir(example_path):
        rmtree(example_path)
