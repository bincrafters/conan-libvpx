#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class LibVPXConan(ConanFile):
    name = "libvpx"
    version = "1.7.0"
    url = "https://github.com/bincrafters/conan-libvpx"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    license = "https://github.com/webmproject/libvpx/blob/master/LICENSE"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        if self.settings.os == 'Windows':
            cygwin_bin = self.deps_env_info['cygwin_installer'].CYGWIN_BIN
            with tools.environment_append({'PATH': [cygwin_bin],
                                           'CONAN_BASH_PATH': os.path.join(cygwin_bin, 'bash.exe')}):
                self.build_configure()
        else:
            self.build_configure()

    def build_configure(self):
        with tools.chdir('sources'):
            win_bash = self.settings.os == 'Windows'
            prefix = os.path.abspath(self.package_folder)
            if self.settings.os == 'Windows':
                prefix = tools.unix_path(prefix, tools.CYGWIN)
            args = ['--prefix=%s' % prefix,
                    '--disable-examples',
                    '--disable-unit-tests',
                    '--enable-vp9-highbitdepth',
                    '--as=yasm']
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            if self.settings.os != 'Windows' and self.options.fPIC:
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
            env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            env_build.configure(args=args, host=False, build=False, target=False)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="LICENSE", src='sources', dst='licenses')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
