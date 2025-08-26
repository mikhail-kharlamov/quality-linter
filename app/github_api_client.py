import logging
from enum import Enum
from pathlib import Path

import requests
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository

from dtos import CommentDto, DirectoryDto, FileDto, PullRequestDto

MAX_FILE_SIZE = 5 * 1024 * 1024


class BranchType(Enum):
    HEAD: str = "head"
    BASE: str = "base"


class GitHubApiClient:
    def __init__(self, token: str):
        self.__gh = Github(token)

    @staticmethod
    def get_diffs(pull_request: PullRequest) -> list[str]:
        diff_url = pull_request.diff_url
        response = requests.get(diff_url)
        diffs = response.text.split("diff --git ")
        return ["diff --git " + diff for diff in diffs]

    @staticmethod
    def is_binary_content(content: str) -> bool:
        if not content:
            return False

        if '\0' in content[:1024]:
            return True

        printable_count = sum(1 for char in content[:4096] if 32 <= ord(char) < 127 or char in '\n\r\t')
        return (printable_count / len(content[:4096])) < 0.7

    def __get_branch_files(self, repo: Repository, pr: PullRequest, branch: BranchType) -> DirectoryDto:
        if branch.value == "base":
            ref = pr.base.ref
        elif branch.value == "head":
            ref = pr.head.ref
        else:
            logging.error(f"Неверный тип ветки: {branch.value}")
            raise ValueError(f"Неверный тип ветки: {branch.value}. Must be in ['base', 'head']")

        # Создаем корневую директорию
        root_dir = DirectoryDto(name="", path="", content=[])

        try:
            contents = repo.get_contents("", ref=ref)

            if isinstance(contents, list):
                for item in contents:
                    item_path = Path(item.path)

                    if item.type == "dir":
                        root_dir.content.append(self.__get_branch_files_recursive(repo, pr, str(item_path), branch))
                    else:
                        try:
                            if item.size > MAX_FILE_SIZE:
                                extension = item_path.suffix[1:].lower() if item_path.suffix else ""

                                root_dir.content.append(
                                    FileDto(
                                        path=item_path,
                                        content=f"[LARGE FILE {item.size // 1024} KB] Download URL: {item.download_url}",
                                        name=file_name,
                                        extension=extension,
                                        is_binary=True
                                    )
                                )
                                continue

                            content, extension, is_binary = self.__get_file_content(item, repo, ref)
                            file_name = item_path.name

                            root_dir.content.append(
                                FileDto(
                                    path=item_path,
                                    content=content,
                                    name=file_name,
                                    extension=extension,
                                    is_binary=is_binary
                                )
                            )
                        except Exception as e:
                            logging.warning(f"Не удалось обработать файл {item_path}: {str(e)}")
                            extension =item_path.suffix[1:].lower() if item_path.suffix else ""

                            root_dir.content.append(
                                FileDto(
                                    path=item_path,
                                    content=f"[ERROR PROCESSING: {str(e)}] Download URL: {item.download_url}",
                                    name=file_name,
                                    extension=extension,
                                    is_binary=True
                                )
                            )
            else:
                try:
                    item_path = Path(contents.path)

                    if contents.size > MAX_FILE_SIZE:
                        extension = item_path.suffix[1:].lower() if item_path.suffix else ""

                        root_dir.content.append(
                            FileDto(
                                path=item_path,
                                content=f"[LARGE FILE {contents.size // 1024} KB] Download URL: {contents.download_url}",
                                name=item_path.name,
                                extension=extension,
                                is_binary=True
                            )
                        )
                    else:
                        content, extension, is_binary = self.__get_file_content(contents, repo, ref)
                        file_name = item_path.name

                        root_dir.content.append(
                            FileDto(
                                path=item_path,
                                content=content,
                                name=file_name,
                                extension=extension,
                                is_binary=is_binary
                            )
                        )
                except Exception as e:
                    logging.warning(f"Не удалось обработать файл {contents.path}: {str(e)}")
                    path = Path(contents.path)
                    extension =path.suffix[1:].lower() if path.suffix else ""

                    root_dir.content.append(
                        FileDto(
                            path=contents.path,
                            content=f"[ERROR PROCESSING: {str(e)}] Download URL: {contents.download_url}",
                            name=path.name,
                            extension=extension,
                            is_binary=True
                        )
                    )

        except Exception as e:
            logging.error(f"Ошибка при получении файлов: {str(e)}")

        return root_dir

    def __get_branch_files_recursive(self, repo: Repository, pr: PullRequest,
                                     path: str, branch: BranchType) -> DirectoryDto:
        if branch.value == "base":
            ref = pr.base.ref
        elif branch.value == "head":
            ref = pr.head.ref
        else:
            logging.error(f"Неверный тип ветки: {branch.value}")
            raise ValueError(f"Неверный тип ветки: {branch.value}. Must be in ['base', 'head']")

        normalized_path = Path(path)
        dir_name = normalized_path.name

        files = DirectoryDto(path=normalized_path, name=dir_name)

        try:
            contents = repo.get_contents(path, ref=ref)
            for item in contents:
                item_path = Path(item.path)

                if item.type == "dir":
                    files.content.append(self.__get_branch_files_recursive(repo, pr, str(item_path), branch))
                else:
                    try:
                        if item.size > MAX_FILE_SIZE:
                            file_name = item_path.name
                            extension = item_path.suffix[1:].lower() if item_path else ""

                            files.content.append(
                                FileDto(
                                    path=item_path,
                                    content=f"[LARGE FILE {item.size // 1024} KB] Download URL: {item.download_url}",
                                    name=file_name,
                                    extension=extension,
                                    is_binary=True
                                )
                            )
                            continue

                        content, extension, is_binary = self.__get_file_content(item, repo, ref)
                        file_name = item_path.name

                        files.content.append(
                            FileDto(
                                path=item_path,
                                content=content,
                                name=file_name,
                                extension=extension,
                                is_binary=is_binary
                            )
                        )
                    except Exception as e:
                        logging.warning(f"Не удалось обработать файл {item_path}: {str(e)}")
                        file_name = item_path.name
                        extension = item_path.suffix[1:].lower() if item_path else ""

                        files.content.append(
                            FileDto(
                                path=item_path,
                                content=f"[ERROR PROCESSING: {str(e)}] Download URL: {item.download_url}",
                                name=file_name,
                                extension=extension,
                                is_binary=True
                            )
                        )
        except Exception as e:
            logging.error(f"Ошибка при рекурсивном получении файлов {normalized_path}: {str(e)}")

        return files

    def __get_file_content(self, file_object, repo, ref: str) -> tuple[str, str, bool]:
        extension = Path(file_object.path).suffix[1:].lower() if file_object.path else ""

        binary_extensions = {
            'exe', 'dll', 'so', 'bin', 'a', 'lib', 'o', 'obj',
            'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'ico', 'psd',
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'zip', 'rar', 'tar', 'gz', '7z', 'bz2', 'xz', 'iso',
            'mp3', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wav', 'aac',
            'db', 'sqlite', 'mdb', 'accdb', 'dbf',
            'jar', 'war', 'ear', 'apk', 'ipa',
            'pyc', 'pyd', 'dylib', 'class', ''
        }
        is_binary = extension in binary_extensions

        content = ""
        try:
            if is_binary:
                return f"[BINARY FILE] Size: {file_object.size} bytes, Download URL: {file_object.download_url}", extension, True

            if file_object.size > MAX_FILE_SIZE:
                return f"[LARGE TEXT FILE {file_object.size // 1024} KB] Download URL: {file_object.download_url}", extension, False

            if file_object.encoding == "base64":
                content = file_object.decoded_content.decode('utf-8', errors='replace')
            elif file_object.download_url:
                response = requests.get(file_object.download_url, stream=True)
                response.raise_for_status()

                content = response.iter_content(
                    chunk_size=1024,
                    decode_unicode=True
                ).__next__()[:MAX_FILE_SIZE]
            else:
                if file_object.type == "file":
                    content = repo.get_contents(file_object.path, ref=ref).decoded_content.decode('utf-8',
                                                                                                  errors='replace')

            if GitHubApiClient.is_binary_content(content):
                is_binary = True
                content = f"[DETECTED BINARY CONTENT] Size: {file_object.size} bytes, Download URL: {file_object.download_url}"

        except UnicodeDecodeError:
            is_binary = True
            content = f"[BINARY CONTENT] Size: {file_object.size} bytes, Download URL: {file_object.download_url}"
        except Exception as e:
            logging.warning(f"Error processing file {file_object.path}: {str(e)}")
            content = f"[ERROR READING FILE: {str(e)}] Size: {file_object.size} bytes, Download URL: {file_object.download_url}"
            is_binary = True

        return content, extension, is_binary

    def __get_files_from_directory(self, directory: DirectoryDto) -> list[FileDto]:
        files = []
        for item in directory.content:
            if isinstance(item, FileDto):
                files.append(item)
            elif isinstance(item, DirectoryDto):
                files.extend(self.__get_files_from_directory(item))
        return files

    def __check_language(self, directory: DirectoryDto, extension: str = "cs") -> bool:
        for item in directory.content:
            if isinstance(item, FileDto) and item.extension == extension:
                return True
            elif isinstance(item, DirectoryDto):
                if self.__check_language(item, extension):
                    return True
        return False

    def get_pull_request_content(self, pull_request: PullRequestDto) -> list[FileDto]:
        owner, repo, pull_number = pull_request.owner, pull_request.repo, pull_request.pull_number
        repo = self.__gh.get_repo(f"{owner}/{repo}")
        pull_request = repo.get_pull(pull_number)
        logging.info(f"Парсинг пул-реквеста {pull_request.title} (#{pull_number}) в репозитории {owner}/{repo.name}")
        branch_directory = self.__get_branch_files(repo, pull_request, BranchType.HEAD)
        files = self.__get_files_from_directory(branch_directory)
        return files

    def post_comments_for_pull_request(self, pull_request: PullRequestDto, comments: list[CommentDto]) -> None:
        owner, repo_name, pull_number = pull_request.owner, pull_request.repo, pull_request.pull_number
        repo = self.__gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pull_number)
        commit_id = list(pr.get_commits())[-1].sha

        logging.info(f"Добавление комментариев к PR #{pull_number} в {owner}/{repo.name}")
        logging.info(f"Количество комментариев: {len(comments)}")

        for comment in comments:
            if not comment.start_line or comment.start_line <= 0:
                logging.warning(f"Пропущен комментарий: некорректный номер начальной строки {comment.start_line}")
                continue
            if not comment.end_line or comment.end_line <= 0:
                logging.warning(f"Пропущен комментарий: некорректный номер последней строки {comment.end_line}")
                continue

            try:
                commit = repo.get_commit(commit_id)

                kwargs = {
                    "body": comment.body,
                    "commit": commit,
                    "path": comment.path,
                    "side": "RIGHT"
                }
                if comment.start_line and comment.start_line != comment.end_line:
                    kwargs["start_line"] = comment.start_line
                    kwargs["line"] = comment.end_line
                else:
                    kwargs["line"] = comment.end_line

                pr.create_review_comment(**kwargs)
                logging.info(f"Комментарий добавлен к {comment.path}")

            except Exception as e:
                logging.error(f"Ошибка при добавлении комментария к {comment.path}: {e}")
