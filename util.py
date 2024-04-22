import os
import subprocess
import sys
import zipfile
from config import CONFIG
from my_types import Function
import hashlib


class Util:
    temp_dir: str
    entry_point: str

    def __init__(self):
        entry = self.get_arguments()["--entry"]
        if not entry:
            print("No entry point found")
            exit(0)
        self.entry_point = entry
        self._create_temp_dir(entry)

    def _create_temp_dir(self, entry: str):
        temp_dir = os.path.join(entry, "__temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        self.temp_dir = temp_dir

    def walk_all_dirs(self) -> list[str]:
        start_path = os.path.realpath(self.entry_point)
        files: list[str] = []
        for root, _dirs, filenames in os.walk(start_path):
            for filename in filenames:
                path = os.path.join(root, filename)
                if path.find("__temp") != -1:
                    continue
                files.append(path)
        return files

    def get_arguments(self) -> dict[str, str]:
        arguments: dict[str, str] = {}
        # Get command line arguments
        for arg in sys.argv[1:]:
            if "=" in arg:
                key, value = arg.split("=")
                arguments[key] = value
            else:
                arguments[arg] = ""
        return arguments

    def parse_path_to_function_name(self, file_path: str) -> Function | bool:
        if not file_path.endswith(".go"):
            return False

        path, name = os.path.split(file_path.replace(self.entry_point, ""))
        api_path = os.path.join(*os.path.split(path)[:-1])
        method = os.path.split(path)[-1]
        name = name.split(".")[0]
        prefix = CONFIG.get("prefix")
        if prefix:
            name = f"{prefix}-{name}"
        out = self.build_code(file_path, name)
        hashing_result = self.compare_hash(out, name)
        print("res", hashing_result)
        # if hashing_result == True:
        #     return False

        self.save_hash(out, name)
        return Function(api_path=api_path, method=method, name=name, binary_path=out)

    def build_code(self, function_path: str, function_name: str) -> str:
        out = os.path.join(self.temp_dir, function_name, "bootstrap")
        command = f'GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -ldflags "-s -w" -o "{out}" "{function_path}"'
        subprocess.run(command, shell=True)
        return out

    def zip_file(self, file: str) -> str:
        output = os.path.join(self.temp_dir, f"{file}.zip")

        with zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zf:
            zf.write(file, arcname=os.path.basename(file))
        return output

    def hash_file(self, file: str) -> str:
        with open(file, "rb") as f:
            data = f.read()
            sha1_hash = hashlib.sha1(data).hexdigest()
        return sha1_hash

    def save_hash(self, file: str, function_name: str) -> str:
        hash = self.hash_file(file)
        hash_data = os.path.join(self.temp_dir, function_name, "hash.sha1")
        with open(hash_data, "w") as f:
            f.write(hash)
        return hash

    def compare_hash(self, file: str, function_name: str) -> bool:
        hash_data = os.path.join(self.temp_dir, function_name, "hash.sha1")

        current_hash = self.hash_file(file)
        if os.path.exists(hash_data):
            with open(hash_data, "r") as f:
                saved_hash = f.read()
            if current_hash == saved_hash:
                return True
        return False

    def create_arn(self, function_name: str):
        return f"arn:aws:lambda:{CONFIG['region']}:{CONFIG['account_id']}:function:{function_name}"


util = Util()
