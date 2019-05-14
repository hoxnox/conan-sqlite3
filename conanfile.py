#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from nxtools import NxConanFile
from conans import CMake, tools


class ConanSqlite3(NxConanFile):
    name = "sqlite3"
    version = "3.28.0"
    description = "Self-contained, serverless, in-process SQL database engine."
    url = "http://github.com/bincrafters/conan-sqlite3"
    homepage = "https://www.sqlite.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Public Domain"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt", "FindSQLite3.cmake"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "threadsafe": [0, 1, 2],
               "enable_column_metadata": [True, False],
               "enable_explain_comments": [True, False],
               "enable_fts3": [True, False],
               "enable_fts4": [True, False],
               "enable_fts5": [True, False],
               "enable_json1": [True, False],
               "enable_rtree": [True, False],
               "omit_load_extension": [True, False]
               }
    default_options = "shared=False",                      \
                      "fPIC=True",                         \
                      "threadsafe=1",                      \
                      "enable_column_metadata=False",      \
                      "enable_explain_comments=False",     \
                      "enable_fts3=False",                 \
                      "enable_fts4=False",                 \
                      "enable_fts5=False",                 \
                      "enable_json1=False",                \
                      "enable_rtree=False",                \
                      "omit_load_extension=False"
    archive_name = ""

    def do_source(self):
        major, minor, patch = self.version.split(".")
        self.archive_name = "sqlite-amalgamation-" + major + minor.rjust(2, "0") + patch.rjust(2, "0") + "00.zip"
        self.retrieve("d02fc4e95cfef672b45052e221617a050b7f2e20103661cda88387349a9b1327",
                [
                    'vendor://sqlite/sqlite3/{archive_name}'.format(archive_name=self.archive_name),
                    'https://www.sqlite.org/2019/{archive_name}'.format(archive_name=self.archive_name)
                ], self.archive_name)
        tools.unzip(self.archive_name)
        os.rename(self.archive_name[:-4], 'sources')


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def do_configure(self):
        del self.settings.compiler.libcxx

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.build_dir = "{staging_dir}/build".format(staging_dir=self.staging_dir)
        tools.unzip(self.archive_name, cmake.build_dir)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.staging_dir
        cmake.definitions["THREADSAFE"] = self.options.threadsafe
        cmake.definitions["ENABLE_COLUMN_METADATA"] = self.options.enable_column_metadata
        cmake.definitions["ENABLE_EXPLAIN_COMMENTS"] = self.options.enable_explain_comments
        cmake.definitions["ENABLE_FTS3"] = self.options.enable_fts3
        cmake.definitions["ENABLE_FTS4"] = self.options.enable_fts4
        cmake.definitions["ENABLE_FTS5"] = self.options.enable_fts5
        cmake.definitions["ENABLE_JSON1"] = self.options.enable_json1
        cmake.definitions["ENABLE_RTREE"] = self.options.enable_rtree
        cmake.definitions["OMIT_LOAD_EXTENSION"] = self.options.omit_load_extension
        cmake.definitions["HAVE_FDATASYNC"] = True
        cmake.definitions["HAVE_GMTIME_R"] = True
        cmake.definitions["HAVE_LOCALTIME_R"] = True
        cmake.definitions["HAVE_POSIX_FALLOCATE"] = True
        cmake.definitions["HAVE_STRERROR_R"] = True
        cmake.definitions["HAVE_USLEEP"] = True
        if self.settings.os == "Windows":
            cmake.definitions["HAVE_LOCALTIME_R"] = False
            cmake.definitions["HAVE_POSIX_FALLOCATE"] = False
        if tools.is_apple_os(self.settings.os):
            cmake.definitions["HAVE_POSIX_FALLOCATE"] = False
        if self.settings.os == "Android":
            cmake.definitions["HAVE_POSIX_FALLOCATE"] = False
        cmake.configure()
        return cmake

    def do_build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def do_package(self):
        self.copy("FindSQLite3.cmake", dst=self.staging_dir)
        cmake = self._configure_cmake()
        cmake.install()

    def do_package_info(self):
        self.cpp_info.libs = ["sqlite3"]
        if self.settings.os == "Linux":
            if self.options.threadsafe:
                self.cpp_info.libs.append("pthread")
            if self.options.omit_load_extension == "False":
                self.cpp_info.libs.append("dl")
