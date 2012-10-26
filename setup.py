#!/usr/bin/python

from distutils.core import setup    
import os

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

packages = find_packages(".")
package_names = packages.keys()

setup(name = "bbciot",
      version = "1.0.0",
      description = "bbciot",
     
      author = "Michael Sparks",
      author_email = "michael.sparks@bbc.co.uk",
      url = "http://www.rd.bbc.co.uk/~michael/",
      license ="Apache Software License",
      packages = package_names,
      package_dir = packages,
      scripts = [
                  'scripts/bbciotservice',
                  'scripts/bbciot_aggregate_analyser',
                  'scripts/bbciot_collator',
                  'scripts/bbciot_reader',
                  'scripts/bbciotservice',
                  'scripts/bbciot.mkdirs',
                ],
      data_files=[
                   ('/etc/init',         ['etc/init/bbciotservice.conf']),
                   ('/etc/bbciotservice', ["etc/bbciotservice/config.json"])
                 ],

      long_description = """
Package for BBC IOT related code.
      """
      )
