from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os, shutil, fnmatch

class LibbsonConan(ConanFile):
    name = "libbson"
    version = "1.13.1"
    url = "https://github.com/theirix/conan-libbson"
    license = "Apache-2.0"
    homepage = "https://github.com/mongodb/mongo-c-driver"
    description = "A BSON utility library."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("https://github.com/mongodb/mongo-c-driver/releases/download/%s/mongo-c-driver-%s.tar.gz"
                  % (self.version, self.version))
        os.rename("mongo-c-driver-%s" % self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build(self):
        cmake = CMake(self)
        # upstream cmake is flawed and doesn't understand boolean values other than ON/OFF
        cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["ENABLE_BSON"] = "ON"
        cmake.definitions["ENABLE_TESTS"] = "OFF"
        cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        cmake.definitions["ENABLE_MONGOC"] = "OFF"
        cmake.definitions["ENABLE_SNAPPY"] = "OFF"
        cmake.definitions["ENABLE_ZLIB"] = "OFF"
        cmake.definitions["ENABLE_UNINSTALL"] = "OFF"
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("copying*", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)

        if not self.options.shared:
            # remove configs for shared libraries
            shutil.rmtree(os.path.join(self.package_folder, 'lib', 'cmake', 'libbson-1.0'), ignore_errors=True)
            if os.path.exists(os.path.join(self.package_folder, 'lib', 'pkgconfig', 'libbson-1.0.pc')):
                os.unlink(os.path.join(self.package_folder, 'lib', 'pkgconfig', 'libbson-1.0.pc'))
            # remove shared libraries
            for root, _, filenames in os.walk(self.package_folder):
                for pattern in ['*.so*', '*.dylib*', '*.dll*']:
                    for filename in fnmatch.filter(filenames, pattern):
                        os.unlink(os.path.join(root, filename))

        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            # remove msvc dlls copied to bin directory
            for root, _, filenames in os.walk(os.path.join(self.package_folder, 'bin')):
                for pattern in ['msvc*.dll']:
                    for filename in fnmatch.filter(filenames, pattern):
                        os.unlink(os.path.join(root, filename))

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
