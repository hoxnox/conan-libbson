from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os, shutil

class LibbsonConan(ConanFile):
    name = "libbson"
    version = "1.9.2"
    url = "https://github.com/theirix/conan-libbson"
    license = "Apache-2.0"
    homepage = "https://github.com/mongodb/libbson"
    description = "A BSON utility library."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("https://github.com/mongodb/libbson/releases/download/%s/libbson-%s.tar.gz"
                  % (self.version, self.version))
        os.rename("libbson-%s" % self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build(self):
        # cmake is supported only for Visual Studio
        use_cmake = self.settings.compiler == "Visual Studio"

        if use_cmake:
            cmake = CMake(self)
            # upstream cmake is flawed and doesn't understand boolean values other than ON/OFF
            cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
            cmake.definitions["ENABLE_TESTS"] = False
            cmake.definitions["CMAKE_INSTALL_PREFIX"] = ("%s/_inst" % self.build_folder)
            cmake.verbose = True
            cmake.configure(source_folder=self.source_subfolder)
            cmake.build()
            cmake.install()

        else:

            env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os == 'Windows')

            # compose configure options
            prefix = os.path.abspath(os.path.join(self.build_folder, "_inst"))
            if self.settings.os == 'Windows':
                prefix = tools.unix_path(prefix)
            configure_args = ['--prefix=%s' % prefix]
            if self.options.shared:
                configure_args.extend(["--enable-shared", "--disable-static"])
            else:
                configure_args.extend(["--disable-shared", "--enable-static"])
            configure_args.extend(["--enable-examples=no", "--enable-tests=no"])

            with tools.chdir(self.source_subfolder):
                # refresh configure
                self.run('autoreconf --force --verbose --install -I build/autotools',
                         win_bash=self.settings.os == 'Windows')

                # disable rpath build
                tools.replace_in_file("configure", r"-install_name \$rpath/", "-install_name ")

                env_build.configure(args=configure_args)

                env_build.make(args=['install'])


    def package(self):
        self.copy("copying*", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        self.copy(pattern="*.h", dst="include", src="_inst/include", keep_path=True)
        # autotools has a bug on mingw: it does not copy bson-stdint.h so copy it manually
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.copy(pattern="bson-stdint.h", dst=os.path.join("include", "libbson-1.0"),
                      src=os.path.join(self.source_subfolder, "build", "cmake", "bson"), keep_path=False)
        if self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", src="_inst/lib", dst="lib", keep_path=False)
            elif self.settings.os == "Windows":
                self.copy(pattern="*.dll*", src="_inst/bin", dst="bin", keep_path=False)
                # mingw dll import libraries: libbson*.dll.a
                self.copy(pattern="*bson*.dll.a", src="_inst/lib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", src="_inst/lib", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*bson*.a", src="_inst/lib", dst="lib", keep_path=False, excludes='*dll*')
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.lib*", src="_inst/lib", dst="lib", keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['bson-1.0']
        else:
            self.cpp_info.libs = ['bson-static-1.0']
        self.cpp_info.includedirs = ['include/libbson-1.0']
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "rt"])
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.extend(["ws2_32"])
                self.cpp_info.defines.append("BSON_STATIC=1")
