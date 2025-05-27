"""
UI文件自动编译器
自动将.ui文件转换为.py文件
"""

import os
import sys
from pathlib import Path
import subprocess


class UICompiler:
    def __init__(self, project_root=None):
        if project_root is None:
            # 获取当前文件所在目录的父目录作为项目根目录
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)

        self.ui_dir = self.project_root / "ui"
        self.src_dir = self.project_root / "src"

    def check_pyuic5(self):
        """检查pyuic5是否可用"""
        try:
            subprocess.run(["pyuic5", "--version"],
                           capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: pyuic5 未找到，请安装 PyQt5-tools")
            print("安装命令: pip install PyQt5-tools")
            return False

    def compile_ui_file(self, ui_file_path, output_file_path):
        """编译单个UI文件"""
        try:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                result = subprocess.run(
                    ["pyuic5", str(ui_file_path)],
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            print(f"✓ 编译成功: {ui_file_path.name} -> {output_file_path.name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 编译失败: {ui_file_path.name}")
            print(f"错误信息: {e.stderr}")
            return False

    def compile_all_ui_files(self):
        """编译所有UI文件"""
        if not self.check_pyuic5():
            return False

        if not self.ui_dir.exists():
            print(f"错误: UI目录不存在: {self.ui_dir}")
            return False

        # 确保src目录存在
        self.src_dir.mkdir(exist_ok=True)

        ui_files = list(self.ui_dir.glob("*.ui"))

        if not ui_files:
            print("警告: 未找到.ui文件")
            return True

        print(f"找到 {len(ui_files)} 个UI文件，开始编译...")

        success_count = 0
        for ui_file in ui_files:
            # 生成对应的Python文件名
            py_filename = f"ui_{ui_file.stem}.py"
            py_file_path = self.src_dir / py_filename

            if self.compile_ui_file(ui_file, py_file_path):
                success_count += 1

        print(f"编译完成: {success_count}/{len(ui_files)} 个文件成功")
        return success_count == len(ui_files)

    def is_ui_newer(self, ui_file, py_file):
        """检查UI文件是否比对应的Python文件更新"""
        if not py_file.exists():
            return True

        ui_mtime = ui_file.stat().st_mtime
        py_mtime = py_file.stat().st_mtime

        return ui_mtime > py_mtime

    def compile_if_needed(self):
        """只编译需要更新的UI文件"""
        if not self.check_pyuic5():
            return False

        if not self.ui_dir.exists():
            print(f"警告: UI目录不存在: {self.ui_dir}")
            return True

        self.src_dir.mkdir(exist_ok=True)

        ui_files = list(self.ui_dir.glob("*.ui"))
        files_to_compile = []

        for ui_file in ui_files:
            py_filename = f"ui_{ui_file.stem}.py"
            py_file_path = self.src_dir / py_filename

            if self.is_ui_newer(ui_file, py_file_path):
                files_to_compile.append((ui_file, py_file_path))

        if not files_to_compile:
            print("所有UI文件都是最新的，无需编译")
            return True

        print(f"需要编译 {len(files_to_compile)} 个文件...")

        success_count = 0
        for ui_file, py_file in files_to_compile:
            if self.compile_ui_file(ui_file, py_file):
                success_count += 1

        print(f"编译完成: {success_count}/{len(files_to_compile)} 个文件成功")
        return success_count == len(files_to_compile)


def main():
    """主函数，用于直接运行此脚本"""
    compiler = UICompiler()

    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        # 强制编译所有文件
        success = compiler.compile_all_ui_files()
    else:
        # 只编译需要更新的文件
        success = compiler.compile_if_needed()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()