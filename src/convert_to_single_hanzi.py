# 2025-12-30  convert_to_single_hanzi.py

from pathlib import Path
from typing import TextIO, Final

# configuration
SRC_PATH: Final = Path(R"C:\Users\ls_ho\AppData\Roaming\Rime\wubi86.custom.dict.yaml")
DEST_PATH: Final = Path(R"C:\Users\ls_ho\AppData\Roaming\Rime\wubi86.custom_single.dict.yaml")
APPEND_COMMENT: Final[list[str]] = [
    "这个文件接下来通过脚本自动过滤了非单字的条目。",
    "这段在文件开头的注释说明也是由脚本自动插入的。",
    "name、version 和 import_tables 将会再次被手动更改。",
]

def is_wubi86_code(code: str) -> bool:
    return 1 <= len(code) <= 4 and 'z' not in code and code.islower()

def is_wubi86_erjian(code: str) -> bool:
    """是 86 五笔二级简码"""
    return len(code) == 2 and is_wubi86_code(code)

def is_non_negative_int(s: str) -> bool:
    return 1 <= len(s) and ((s[0] != '0' and s.isdigit()) or s == '0')

def write_append_comment(dest: TextIO) -> None:
    dest.write('\n')
    for line in APPEND_COMMENT:
        dest.write(f"# {line}\n")
    dest.write('\n')

def convert(src: TextIO, dest: TextIO) -> None:
    """
    从 `src` 读入内容，写入 `dst` ，但：
    在 --- 之前的部分，追加一段说明注释。
    对于数据部分，假定不存在 '#' 注释。忽略空行。只保留单字的条目。
    行的格式是 text TAB code TAB freq [ TAB another_code ]。
    """

    # 读取 --- 之前的部分，但在最后追加一段说明注释。
    while (line := src.readline()):
        if line.startswith("---"):
            write_append_comment(dest)
            dest.write(line)
            break
        dest.write(line)

    # 读取 ... 之前的部分，全部写入 dst 。
    while (line := src.readline()):
        if line.startswith("..."):
            dest.write(line)
            break
        dest.write(line)

    # 读取 ... 之后的部分，
    while (line := src.readline()):
        assert '#' not in line
        line = line.strip()
        if not line:
            dest.write('\n')
            continue

        text, code, freq, *rest = line.split("\t")

        assert is_wubi86_code(code)
        assert is_non_negative_int(freq)
        assert len(rest) == 0 or (len(rest) == 1 and is_wubi86_erjian(rest[0]))

        if len(text) == 1:
            dest.write(line + "\n")


def main() -> None:
    if not SRC_PATH.exists():
        print(f"Input file {SRC_PATH} does not exist.")
        exit(1)

    if DEST_PATH.exists():
        print(f"Output file {DEST_PATH} already exists.")
        print("Overwrite? (y/n)")
        if input().lower() != "y":
            exit(0)

    with SRC_PATH.open("r", encoding="utf-8") as src_file:
        with DEST_PATH.open("w", encoding="utf-8") as dest_file:
            convert(src_file, dest_file)

    print(f"Successfully converted {SRC_PATH} -> {DEST_PATH}.")
    print()
    print("Do not forget to modify the:\n"
          "    - name (both in yaml section and name section)\n"
          "    - version (in yaml section)\n"
          "    - import_tables (in yaml section)\n"
          "of dictionary file manually.\n")

if __name__ == "__main__":
    main()
