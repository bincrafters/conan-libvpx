# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException
import os
import shutil


class LibVPXConan(ConanFile):
    name = "libvpx"
    version = "1.8.0"
    url = "https://github.com/bincrafters/conan-libvpx"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    topics = ("conan", "vpx", "codec", "web", "VP8", "VP9")
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _source_subfolder = "source_subfolder"


    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanException('Windows shared builds are not supported')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires('yasm_installer/1.3.0@bincrafters/stable')
        if tools.os_info.is_windows:
            self.build_requires('msys2_installer/20161025@bincrafters/stable')

    def source(self):
        source_url = "https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version
        tools.get(source_url, sha256="86df18c694e1c06cc8f83d2d816e9270747a0ce6abe316e93a4f4095689373f6")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _fix_sources(self):
        gen_vcxproj = os.path.join(self._source_subfolder, 'build', 'make', 'gen_msvs_vcxproj.sh')
        tools.replace_in_file(gen_vcxproj,
                              '        --help|-h) show_help',
                              '        --help|-h) show_help\n        ;;\n'
                              '        -O*) echo "ignoring $opt..."\n')
        tools.replace_in_file(gen_vcxproj,
                              '        --help|-h) show_help',
                              '        --help|-h) show_help\n        ;;\n'
                              '        -Zi) echo "ignoring $opt..."\n')
        tools.replace_in_file(gen_vcxproj,
                              '        --help|-h) show_help',
                              '        --help|-h) show_help\n        ;;\n'
                              '        -MD*|-MT*) echo "ignoring $opt (this option is already handled)"\n')
        # disable warning:
        # vpx.lib(vpx_src_vpx_image.obj) : MSIL .netmodule or module compiled with /GL found; restarting link
        # with /LTCG; add /LTCG to the link command line to improve linker performance
        tools.replace_in_file(gen_vcxproj,
                              'tag_content WholeProgramOptimization true',
                              'tag_content WholeProgramOptimization false')

        # Enable Visual Studio 2019
        tools.replace_in_file(os.path.join(self._source_subfolder, 'configure',),
                              'all_platforms="${all_platforms} x86_64-win64-vs15"',
                              'all_platforms="${all_platforms} x86_64-win64-vs15"\n'
                              'all_platforms="${all_platforms} x86_64-win64-vs16"')
        tools.replace_in_file(gen_vcxproj,
                              '10|11|12|14|15',
                              '10|11|12|14|15|16')
        tools.replace_in_file(gen_vcxproj,
                              '            if [ "$vs_ver" = "15" ]; then\n'
                              '                tag_content PlatformToolset v141\n'
                              '            fi',
                              '            if [ "$vs_ver" = "15" ]; then\n'
                              '                tag_content PlatformToolset v141\n'
                              '            fi\n'
                              '            if [ "$vs_ver" = "16" ]; then\n'
                              '                tag_content PlatformToolset v142\n'
                              '            fi')
        gen_sln = os.path.join(self._source_subfolder, 'build', 'make', 'gen_msvs_sln.sh')
        tools.replace_in_file(gen_sln,
                              '10|11|12|14|15',
                              '10|11|12|14|15|16')
        tools.replace_in_file(gen_sln,
                              '    15) sln_vers="12.00"\n'
                              '       sln_vers_str="Visual Studio 2017"\n'
                              '    ;;',
                              '    15) sln_vers="12.00"\n'
                              '       sln_vers_str="Visual Studio 2017"\n'
                              '    ;;\n'
                              '    16) sln_vers="12.00"\n'
                              '       sln_vers_str="Visual Studio 2019"\n'
                              '    ;;')

    def _configure_autotools(self):
        win_bash = tools.os_info.is_windows
        prefix = os.path.abspath(self.package_folder)
        if self.settings.os == 'Windows':
            prefix = tools.unix_path(prefix, tools.CYGWIN)
        args = ['--prefix=%s' % prefix,
                '--disable-examples',
                '--disable-unit-tests',
                # '--disable-tools',
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
        if self.settings.compiler == 'Visual Studio':
            if 'MT' in str(self.settings.compiler.runtime):
                args.append('--enable-static-msvcrt')

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
        if self.settings.compiler == 'apple-clang':
            if float(str(self.settings.compiler.version)) < 8.0:
                args.append('--disable-avx512')
        with tools.vcvars(self.settings):
            env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)
            env_build.configure(args=args, configure_dir=self._source_subfolder, host=False, build=False, target=False)
        return env_build

    def build(self):
        self._fix_sources()
        with tools.vcvars(self.settings):
            env_build = self._configure_autotools()
            env_build.make()

    def package(self):
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        env_build.install()

        self.copy(pattern="LICENSE", src='sources', dst='licenses')
        if self.settings.os == 'Windows':
            name = 'vpxmt.lib' if 'MT' in str(self.settings.compiler.runtime) else 'vpxmd.lib'
            if self.settings.arch == 'x86_64':
                libdir = os.path.join(self.package_folder, 'lib', 'x64')
            elif self.settings.arch == 'x86':
                libdir = os.path.join(self.package_folder, 'lib', 'Win32')
            shutil.move(os.path.join(libdir, name), os.path.join(self.package_folder, 'lib', 'vpx.lib'))
        shutil.rmtree(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
