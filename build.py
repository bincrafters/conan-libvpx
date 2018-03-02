#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared
import platform
import os

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=True)

    for settings, options, env_vars, build_requires, reference in builder.items:
        if build_shared.get_os() == "Windows":
            installers = ["cygwin_installer/2.9.0@bincrafters/stable", "yasm_installer/1.3.0@bincrafters/stable"]
            if os.getenv('MINGW_CONFIGURATIONS', ''):
                installers.append("mingw_installer/1.0@conan/stable")
            build_requires.update({"*": installers})

    builder.run()
