import os
import shutil
from glob import glob
from pathlib import Path


class PathUtil:
    @staticmethod
    def get_root_path():
        """
            - retorna: O caminho raiz do programa
        """
        root_path = os.getcwd()
        return root_path

    @staticmethod
    def get_dirs(root_path):
        """
            - retorna: Retorna todas as pastas de um path raiz
        """
        return [filepath.path for filepath in os.scandir(root_path) if filepath.is_dir()]

    @staticmethod
    def get_files(root_path, extension='*.*'):
        """
            - root_path: Path raiz a partir de onde serão realizadas a busca
            - extension: Extensão de arquivo usado para filtrar o retorno
            - retorna: Retorna todos os arquivos recursivamente a partir de um path raiz
         """
        return [y for x in os.walk(root_path) for y in glob(os.path.join(x[0], extension))]

    @staticmethod
    def get_dirname(root_path):
        """
            - root_path: Path completo da pasta
            - retorna: somente o nome da última pasta do path
        """
        return os.path.basename(os.path.normpath(root_path))

    @staticmethod
    def get_filename(file_path):
        """
            - file_path: Path completo de um arquivo
            - retorna: somente o nome do arquivo
        """
        return file_path.split(os.path.sep)[-1]

    @staticmethod
    def join(*paths):
        """
            - paths: lista de paths que serão concatenados
            - retorna: path concatenado
        """
        complete_path = ''
        for path in paths:
            complete_path = os.path.join(complete_path, path)
        return complete_path

    @staticmethod
    def build_path(*paths):
        """
            - paths: parametros contendo cada path.
            - retorna: o path construido a partir do root path mais os parametros passados
        """
        complete_path = PathUtil.get_root_path()
        for path in paths:
            complete_path = f'{complete_path}/{path}'
        return complete_path

    @staticmethod
    def create_dir(root_path, foldername):
        """
            - root_path: Path completo onde a pasta será criada
            - foldername: Nome da pasta que será criada
            - retorna: o path completo da pasta criada
        """
        target_path = os.path.join(root_path, foldername)
        Path(target_path).mkdir(parents=True, exist_ok=True)
        return target_path

    @staticmethod
    def remove_dir(folder_path):
        """
            - folder_path: Path completo da pasta que será removida e todos os arquivos que nela contiver
        """
        shutil.rmtree(folder_path)
