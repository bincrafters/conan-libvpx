#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class LibnameConan(ConanFile):
    name = "libvpx"
    version = "1.6.1"
    url = "https://github.com/bincrafters/conan-libvpx"
    description = "WebM VP8/VP9 Codec SDK"
    license = "https://github.com/webmproject/libvpx/blob/master/LICENSE"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def build_requirements(self):
        self.build_requires("yasm_installer/[>=1.3.0]@bincrafters/stable")

    def source(self):
        source_url = "https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        with tools.chdir('sources'):
            args = ['--prefix=%s' % self.package_folder,
                    '--disable-examples',
                    '--disable-unit-tests',
                    '--enable-vp9-highbitdepth',
                    '--as=yasm']
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            if self.settings.build_type == "Debug":
                args.append('--enable-debug')
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args, host=False, build=False, target=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="LICENSE", src='sources')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
