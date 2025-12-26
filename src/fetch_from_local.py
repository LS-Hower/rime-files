from __future__ import annotations
from typing import TypedDict, NotRequired, Optional
from collections.abc import Callable
from itertools import takewhile
import os

# 允许自定义文件获取方式。
type FileFetcher = Callable[[str], str]
type FileNameModifier = Callable[[str], str]
type FileDescription = str | tuple[str, FileFetcher, FileNameModifier]

# 用类 JSON 方式描述文件夹结构。
class FolderDescription(TypedDict):
    name: str
    files: NotRequired[list[FileDescription]]
    folders: NotRequired[list[FolderDescription]]

def make_prefix_adder(prefix: str) -> FileNameModifier:
    def adder(filename: str) -> str:
        return prefix + filename
    return adder

def default_file_fetcher(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def default_filename_modifier(filename: str) -> str:
    return filename

def fetch_wubi86_custom_dict(filename: str) -> str:
    assert filename.endswith('wubi86.custom.dict.yaml'), "The fetcher designed for wubi86.custom.dict.yaml is not used on it."

    # 读取，直到遇到 '...\n' 行为止。
    with open(filename, 'r', encoding='utf-8') as f:
        return ''.join(takewhile(lambda line: line != '...\n', f)) + '...\n'

def fetch_single_file(source_path: str, source_file_name: str,
                      dest_path: str, dest_file_name: str,
                      fetcher: FileFetcher = default_file_fetcher) -> None:
    src = os.path.join(source_path, source_file_name)
    dest = os.path.join(dest_path, dest_file_name)

    try:
        content = fetcher(src)
        # 检查要写入的内容是否过大

        if len(content) > 10 * 1024 * 1024:
            print(f'[Warning] Content fetched from {src} is large: {len(content)} bytes')
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f'[Error] "{e}" occured when fetching {src} -> {dest}')

def get_folder_files(folder: str) -> tuple[str, list[str]]:
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return folder, files

def find_from_sources(filename: str, sources: dict[str, list[str]]) -> Optional[str]:
    for path, files in sources.items():
        if filename in files:
            return path
    return None

def fetch_from_local(structure: FolderDescription, source_paths: list[str]) -> None:
    """
    从指定的本地路径 `source_paths` 中读取文件，复制到由 `structure` 描述的目录结构中。
    `structure` 中可能存在自定义的文件读取函数。
    `source_paths` 中靠前的路径优先级更高。

    复制成功 / 失败时打印日志。
    若文件过大，打印日志。
    """

    # 获取 source_paths 中所有文件名

    sources = dict(get_folder_files(path) for path in source_paths)

    def fetch_folder_recursive(dest_description: FolderDescription, dest_parent_path: str) -> None:
        """递归复制一个文件夹。"""

        # 先确定要往哪里复制；如果不存在就创建
        dest_current_path = os.path.normpath(os.path.join(dest_parent_path, dest_description['name']))
        if not os.path.exists(dest_current_path):
            os.makedirs(dest_current_path)

        # 复制各个文件
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
                    print(f'[Warning] Could not find {os.path.join(dest_current_path, source_filename)} in sources. Skipped.')
                    continue

                # 找到了；复制该文件
                dest_filename = name_modifier(source_filename)
                print(f'[Info] Fetching: {source_filename} -> {dest_filename} (paths: {source_path} -> {dest_current_path})')
                fetch_single_file(
                    source_path, source_filename,
                    dest_current_path, dest_filename,
                    fetcher,
                )

        # 复制各个子文件夹
        if 'folders' in dest_description:
            for sub_folder in dest_description['folders']:
                fetch_folder_recursive(sub_folder, dest_current_path)

    fetch_folder_recursive(structure, '.')

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
        ]
    }

    fetch_from_local(
        rime_structure,
        [
            "C:\\Users\\ls_ho\\AppData\\Roaming\\Rime",
        ],
    )

