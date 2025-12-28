from __future__ import annotations
from collections.abc import Callable, Generator
from dataclasses import dataclass
from itertools import takewhile
from pathlib import Path
from typing import NotRequired, Optional, TypedDict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 允许自定义文件获取方式。
type FileName = str
type FileContent = str
type FolderName = str
type FileFetcher = Callable[[Path], str]
type FileNameModifier = Callable[[FileName], FileName]
type FileDescription = FileName | tuple[FileName, FileFetcher, FileNameModifier]

# 用类 JSON 方式描述文件夹结构。
class FolderDescription(TypedDict):
    name: FolderName
    files: NotRequired[list[FileDescription]]
    folders: NotRequired[list[FolderDescription]]

def make_prefix_adder(filename_prefix: str) -> FileNameModifier:
    """
    纯函数。
    `make_prefix_adder('partial-')('test.txt')` -> `'partial-test.txt'`
    """
    def adder(filename: FileName) -> FileName:
        return filename_prefix + filename
    return adder

def default_filename_modifier(filename: FileName) -> FileName:
    """纯函数。"""
    return filename

def find_from_sources(filename: FileName, sources: dict[Path, set[FileName]]) -> Optional[Path]:
    """
    纯函数。
    在 `sources` 的值中查找 `filename`，返回 `sources` 的键。
    如果找不到，返回 `None`。
    """
    for path, files in sources.items():
        if filename in files:
            return path
    return None

def default_file_fetcher(file: Path) -> FileContent:
    """
    不是纯函数：需要读取本地文件内容。
    读取一个文件的内容。
    """
    assert file.is_file()
    return file.read_text(encoding='utf-8')

def fetch_wubi86_custom_dict(file: Path) -> FileContent:
    """
    不是纯函数：需要读取本地文件内容。
    专为 `wubi86.custom.dict.yaml` 设计的文件读取函数。
    只读取文件头，直到遇到 `'...\n'` 行为止。
    `'...\n'` 行也会追加到返回的字符串中。
    """
    assert file.is_file()
    assert file.name == 'wubi86.custom.dict.yaml', "The fetcher designed for wubi86.custom.dict.yaml is not used on it."

    with file.open('r', encoding='utf-8') as f:
        return ''.join(takewhile(lambda line: line != '...\n', f)) + '...\n'

@dataclass
class FileFetchTask(object):
    source: Path
    destination: Path
    fetcher: FileFetcher = default_file_fetcher

    def __call__(self: FileFetchTask) -> None:
        """
        不是纯函数：需要读取和写入本地文件。
        执行由 `self` 描述的任务：用 `fetcher` 从 `source` 中读取文件内容，写入到 `destination` 中。
        """
        logger.info(f'Fetching: {self.source} -> {self.destination}')
        assert self.source.is_file()

        try:
            # 如果目标文件夹不存在，创建它
            if not self.destination.parent.exists():
                self.destination.parent.mkdir(parents=True, exist_ok=False)
                logger.info(f'Created directory: {self.destination.parent}')
            content = self.fetcher(self.source)
            # 检查要写入的内容是否过大
            if len(content) > 1 * 1024 * 1024:
                kb = len(content) / 1024
                logger.warning(f'Content fetched from {self.source} is large: {kb:.2f} KB')
            self.destination.write_text(content, encoding='utf-8')

            assert self.destination.is_file()

        except Exception as e:
            logger.error(f'An error "{e}" occured when fetching {self.source} -> {self.destination}')


def iter_fetch_tasks(structure: FolderDescription, source_paths: list[Path]) -> Generator[FileFetchTask]:
    """
    不是纯函数：需要读取本地的文件结构。

    依据 `structure`，从指定的本地路径 `source_paths` 中寻找哪些文件可以复制，应该复制到什么地方。
    `structure` 中可能存在自定义的文件读取函数。
    `source_paths` 中靠前的路径优先级更高。
    返回所有要执行的任务（以生成器形式）。

    复制成功 / 失败时打印日志。
    若文件过大，打印日志。
    """

    # 获取 source_paths 中所有文件名
    sources: dict[Path, set[FileName]] = {
        path: {
            sub.name
            for sub in path.iterdir()
            if sub.is_file()
        }
        for path in source_paths
    }

    def iter_folder_recursive(dest_description: FolderDescription, dest_parent_path: Path) -> Generator[FileFetchTask]:
        """
        不是纯函数：需要读取本地的文件结构。
        递归生成对于一个文件夹的任务。
        """

        dest_current_path = dest_parent_path / dest_description['name']

        # 生成复制各个文件的任务
        if 'files' in dest_description:
            for source_file_description in dest_description['files']:
                if isinstance(source_file_description, str):
                    source_filename, fetcher, name_modifier = source_file_description, default_file_fetcher, default_filename_modifier
                elif isinstance(source_file_description, tuple):
                    source_filename, fetcher, name_modifier = source_file_description
                else:
                    assert False, f'file {source_file_description} is not a string or tuple; got {type(source_file_description)}'

                # 在各个来源文件夹中寻找文件
                source_path = find_from_sources(source_filename, sources)

                # 没能找到
                if source_path is None:
                    logger.error(f'Could not find {dest_current_path / source_filename} in sources. Skipped.')
                    continue

                # 找到了；生成“复制该文件”的任务
                dest_filename = name_modifier(source_filename)
                task = FileFetchTask(
                    source = source_path / source_filename,
                    destination = dest_current_path / dest_filename,
                    fetcher = fetcher
                )

                yield task

        # 对于子文件夹递归处理
        if 'folders' in dest_description:
            for sub_folder in dest_description['folders']:
                yield from iter_folder_recursive(sub_folder, dest_current_path)

    yield from iter_folder_recursive(structure, Path('.'))

if __name__ == '__main__':

    rime_structure: FolderDescription = {
        'name': '../files',
        'files': [
            'symbols.custom.yaml',
            'wubi86.custom.yaml',
            'wubi86.schema.yaml',
            'weasel.custom.yaml',
            'default.custom.yaml',
        ],
        'folders': [
            {
                'name': 'dicts',
                'files': [
                    ('wubi86.custom.dict.yaml', fetch_wubi86_custom_dict, make_prefix_adder('partial-')),
                    'wubi86.109.dict.yaml',
                    'wubi86.hower.dict.yaml',
                    'wubi86.skana.dict.yaml',
                    'wubi86.touhou.dict.yaml',
                    'wubi86.yijian_ext.dict.yaml',
                    'wubi86.zkana.dict.yaml',
                ],
            },
        ],
    }

    sources = [
        Path("C:\\Users\\ls_ho\\AppData\\Roaming\\Rime"),
    ]

    for task in iter_fetch_tasks(rime_structure, sources):
        task()


