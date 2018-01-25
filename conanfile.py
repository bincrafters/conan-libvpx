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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

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
            if self.options.fPIC:
                args.append('--enable-pic')
            if self.settings.build_type == "Debug":
                args.append('--enable-debug')

            arch = {'x86': 'x86',
                    'x86_64': 'x86_64',
                    'armv7': 'armv7',
                    'armv8': 'arm64',
                    'mips': 'mips32',
                    'mips64': 'mips64',
                    'sparc': 'sparc'}.get(str(self.settings.arch))
            if self.settings.compiler == 'Visual Studio':
                compiler = 'vs' + str(self.settings.compiler.version)
            else:
                compiler = 'gcc'
            if self.settings.os == 'Windows':
                os_name = 'win32' if self.settings.arch == 'x86' else 'win64'
            elif str(self.settings.os) in ['Macos', 'iOS', 'watchOS', 'tvOS']:
                os_name = 'darwin9'
            elif self.settings.os == 'Linux':
                os_name = 'linux'
            elif self.settings.os == 'Solaris':
                os_name = 'solaris'
            elif self.settings.os == 'Android':
                os_name = 'android'
            target = "%s-%s-%s" % (arch, os_name, compiler)
            args.append('--target=%s' % target)
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args, host=False, build=False, target=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="LICENSE", src='sources')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
