import glob
import os
import shutil
from os import path

from .path import PathUtil


class DirectoryUtil:
    def __init__(self, working_directory):
        self.working_directory = working_directory
        self.file_system = FileSystem()

    def create_directory(self, directory):
        directory_path = PathUtil.build_path(self.working_directory, directory)
        self.file_system.create_directory(directory_path)

    def is_there_directory(self, directory):
        directory_path = PathUtil.build_path(self.working_directory, directory)
        return self.file_system.is_there_file_or_directory(directory_path)

    def get_directories(self, directory=None):
        directory_path = self.working_directory if directory is None else PathUtil.build_path(self.working_directory, directory)
        return self.file_system.get_directories(directory_path)

    def delete_directory(self, directory):
        directory_path = PathUtil.build_path(self.working_directory, directory)
        self.file_system.delete_directory_and_files(directory_path)


class FileManager:
    def __init__(self, working_directory):
        self.working_directory = working_directory
        self.file_system = FileSystem()

    def is_there_file(self, file_path):
        directory_path = PathUtil.build_path(self.working_directory, file_path)
        return self.file_system.is_there_file_or_directory(directory_path)

    def get_files(self, directory):
        directory_path = PathUtil.build_path(self.working_directory, directory)
        return self.file_system.get_files(directory_path)


class FileSystem:
    @staticmethod
    def create_directory(directory_path):
        os.mkdir(directory_path)

    @staticmethod
    def is_there_file_or_directory(file_or_directory_path):
        return path.exists(file_or_directory_path)

    @staticmethod
    def get_directories(directory_path):
        directories = []
        for file_or_directory in os.listdir(directory_path):
            file_or_directory_path = os.path.join(directory_path, file_or_directory)
            if os.path.isdir(file_or_directory_path):
                directories.append(file_or_directory)
        directories.sort()
        return directories

    @staticmethod
    def get_files(directory_path):
        files = []
        for file_or_directory in os.listdir(directory_path):
            file_or_directory_path = os.path.join(directory_path, file_or_directory)
            if os.path.isfile(file_or_directory_path):
                files.append(file_or_directory)
        return files

    @staticmethod
    def get_recursive_files(directory_path_pattern):
        return glob.glob(directory_path_pattern, recursive=True)

    @staticmethod
    def delete_directory_and_files(directory_path):
        shutil.rmtree(directory_path)
