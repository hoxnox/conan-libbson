[ ![Download](https://api.bintray.com/packages/theirix/conan-repo/libbson%3Atheirix/images/download.svg) ](https://bintray.com/theirix/conan-repo/libbson%3Atheirix/_latestVersion)
[![Build Status](https://travis-ci.org/theirix/conan-libbson.svg)](https://travis-ci.org/theirix/conan-libbson)
[![Build status](https://ci.appveyor.com/api/projects/status/github/bincrafters/conan-libbson?svg=true)](https://ci.appveyor.com/project/theirix/conan-libbson)

# conan-libbson

[Conan.io](https://conan.io) package for [libbson](https://github.com/mongodb/mongo-c-driver) library

The packages generated with this **conanfile** can be found in [bintray](https://bintray.com/theirix/conan-repo/libbson%3Atheirix).

## Build packages

    $ pip install conan_package_tools
    $ python build.py
    
## Reuse the packages

### Basic setup

    $ conan install libbson/<pkg_version>@theirix/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    libbson/<pkg_version>@theirix/stable

    [options]
    libbson:shared=True # false
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
