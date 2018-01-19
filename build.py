from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="libbson:shared", pure_c=True)

    builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        # skip mingw cross-builds
        if not (platform.system() == "Windows" and settings["compiler"] == "gcc" and settings["arch"] == "x86"):
            # add msys2 as a build requirement for mingw builds
            if platform.system() == "Windows" and settings["compiler"] == "gcc":
                build_requires["*"] = build_requires.get("*", []) + ['msys2_installer/latest@bincrafters/stable']
            builds.append([settings, options, env_vars, build_requires])
    builder.builds = builds

    builder.run()
