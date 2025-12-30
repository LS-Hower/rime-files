from __future__ import annotations
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, Optional, TypedDict
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

type FileName = str
type FolderName = str

# 用类 JSON 方式描述文件夹结构。
class FolderDescription(TypedDict):
    name: FolderName
    files: NotRequired[list[FileName]]
    folders: NotRequired[list[FolderDescription]]

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

@dataclass
class FileFetchTask(object):
    source: Path
    destination: Path

    def __call__(self: FileFetchTask) -> None:
        """
        不是纯函数：需要读取和写入本地文件。
        执行由 `self` 描述的任务：从 `source` 中读取文件内容，写入到 `destination` 中。
        """
        logger.info(f'Fetching: {self.source} -> {self.destination}')
        assert self.source.is_file()

        try:
            # 如果目标文件夹不存在，创建它
            if not self.destination.parent.exists():
                self.destination.parent.mkdir(parents=True, exist_ok=False)
                logger.info(f'Created directory: {self.destination.parent}')
            # 检查文件是否过大
            size = self.source.stat().st_size
            if size > 1 * 1024 * 1024:
                mb = size / (1024 * 1024)
                logger.warning(f'Content fetched from {self.source} is large: {mb:.2f} KB')
            # 复制文件
            shutil.copy(self.source, self.destination)

            assert self.destination.is_file()

        except Exception as e:
            logger.error(f'An error "{e}" occured when fetching {self.source} -> {self.destination}')


def iter_fetch_tasks(structure: FolderDescription, source_paths: list[Path]) -> Generator[FileFetchTask]:
    """
    不是纯函数：需要读取本地的文件结构。

    依据 `structure`，从指定的本地路径 `source_paths` 中寻找哪些文件可以复制，应该复制到什么地方。
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
            for source_filename in dest_description['files']:

                # 在各个来源文件夹中寻找文件
                source_path = find_from_sources(source_filename, sources)

                # 没能找到
                if source_path is None:
                    logger.error(f'Could not find {dest_current_path / source_filename} in sources. Skipped.')
                    continue

                # 找到了；生成“复制该文件”的任务
                dest_filename = source_filename
                task = FileFetchTask(
                    source = source_path / source_filename,
                    destination = dest_current_path / dest_filename,
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
                    'wubi86.109.dict.yaml',
                    'wubi86.custom.dict.yaml',
                    'wubi86.custom_single.dict.yaml',
                    'wubi86.dict.yaml',
                    'wubi86.hower.dict.yaml',
                    #'wubi86.hower_private.dict.yaml',
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


