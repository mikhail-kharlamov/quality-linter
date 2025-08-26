import json
import logging
from pathlib import Path

from dtos import DirectoryDto, FileDto


class Parser:
    @staticmethod
    def enumerate_lines(text: str) -> str:
        lines = text.split('\n')
        if not lines or len(lines) == 0:
            return text

        enumerated_lines = []
        for i in range(len(lines)):
            enumerated_lines.append(f"{i + 1} {lines[i]}")

        return '\n'.join(enumerated_lines)

    @staticmethod
    def enumerate_lines_separately(text: str) -> list[tuple[int, str]]:
        lines = text.split('\n')
        if not lines or len(lines) == 0:
            return []

        enumerated_lines = []
        for i in range(len(lines)):
            enumerated_lines.append((i + 1, lines[i]))

        return enumerated_lines

    @staticmethod
    def get_directory_from_json(path: str, enumerate_code_lines: bool = False) -> DirectoryDto:
        """Получает структуру директории из JSON файла"""
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            content = [FileDto.from_dict(file) for file in data]
            for file in content:
                if enumerate_code_lines and not file.is_binary:
                    file.content = Parser.enumerate_lines(file.content)
            return DirectoryDto(content=content)
        except Exception as e:
            logging.error(f"Ошибка при чтении JSON файла {path}: {str(e)}")
            raise ValueError(f"Не удалось прочитать JSON файл: {str(e)}") from e

    def parse_directory_dto(self, directory: DirectoryDto) -> str:
        files_content = ""

        for obj in directory.content:
            if isinstance(obj, DirectoryDto):
                children_content: str = self.parse_directory_dto(obj)
                files_content += children_content
            elif isinstance(obj, FileDto):
                if not obj.is_binary:
                    files_content += f"{obj.path}:\n{obj.content}\n\n"
        return files_content

    def parse_directory(self, root_path: str) -> DirectoryDto:
        """Парсит локальную директорию и возвращает её структуру в виде DirectoryDto"""
        path: Path = Path(root_path).absolute()
        return self._parse_directory_recursive(path=path, root_path=path)

    def _parse_directory_recursive(self, path: Path, root_path: Path) -> DirectoryDto:
        """Рекурсивно парсит директорию и её поддиректории"""
        dir_name = path.name
        dir_path = str(path.relative_to(root_path))

        directory = DirectoryDto(name=dir_name, path=dir_path, content=[])

        try:
            for item in path.iterdir():
                if item.is_dir():
                    directory.content.append(self._parse_directory_recursive(item, root_path))
                else:
                    try:
                        directory.content.append(self._parse_file(item, root_path))
                    except Exception as e:
                        logging.warning(f"Не удалось обработать файл {item}: {str(e)}")
                        directory.content.append(
                            self._create_error_file_dto(item, root_path, f"[ERROR PROCESSING: {str(e)}]")
                        )
        except Exception as e:
            logging.error(f"Ошибка при чтении директории {path}: {str(e)}")

        return directory

    def _parse_file(self, file_path: Path, root_path: Path, enumerate_code_lines: bool = False) -> FileDto:
        """Парсит файл и возвращает FileDto"""
        relative_path = str(file_path.relative_to(root_path))
        file_name = file_path.name
        extension = file_path.suffix[1:].lower() if file_path.suffix else ""

        file_size = file_path.stat().st_size
        is_binary = self._is_binary_file(file_path)

        if is_binary:
            return FileDto(
                path=relative_path,
                content=f"[BINARY FILE] Size: {file_size} bytes",
                name=file_name,
                extension=extension,
                is_binary=True
            )

        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            if enumerate_code_lines:
                content = Parser.enumerate_lines(content)
            return FileDto(
                path=relative_path,
                content=content,
                name=file_name,
                extension=extension,
                is_binary=False
            )
        except UnicodeDecodeError:
            return FileDto(
                path=relative_path,
                content=f"[BINARY CONTENT] Size: {file_size} bytes",
                name=file_name,
                extension=extension,
                is_binary=True
            )
        except Exception as e:
            return self._create_error_file_dto(file_path, root_path, f"[ERROR READING FILE: {str(e)}]")

    def _create_error_file_dto(self, file_path: Path, root_path: Path, error_msg: str) -> FileDto:
        """Создает FileDto для файла с ошибкой"""
        relative_path = str(file_path.relative_to(root_path))
        file_name = file_path.name
        extension = file_path.suffix[1:].lower() if file_path.suffix else ""

        return FileDto(
            path=relative_path,
            content=error_msg,
            name=file_name,
            extension=extension,
            is_binary=True
        )

    def _is_binary_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл бинарным"""
        try:
            binary_extensions = {
                'exe', 'dll', 'so', 'bin', 'a', 'lib', 'o', 'obj',
                'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'ico', 'psd',
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'zip', 'rar', 'tar', 'gz', '7z', 'bz2', 'xz', 'iso',
                'mp3', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wav', 'aac',
                'db', 'sqlite', 'mdb', 'accdb', 'dbf',
                'jar', 'war', 'ear', 'apk', 'ipa',
                'pyc', 'pyd', 'dylib', 'class'
            }
            extension = file_path.suffix[1:].lower()
            if extension in binary_extensions:
                return True

            with file_path.open('rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True

                printable_count = sum(1 for byte in chunk if 32 <= byte < 127 or byte in b'\n\r\t')
                return (printable_count / len(chunk)) < 0.7 if chunk else False

        except Exception:
            return True
