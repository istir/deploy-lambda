import hashlib
import os


class Hash:
    def __init__(self) -> None:
        pass

    def hash_file(self, file: str) -> str:
        with open(file, "rb") as f:
            data = f.read()
            sha1_hash = hashlib.sha1(data).hexdigest()
        return sha1_hash

    def save_hash(self, file: str, save_path: str) -> str:
        hash = self.hash_file(file)
        hash_data = os.path.join(save_path, "hash.sha1")
        with open(hash_data, "w") as f:
            f.write(hash)
        return hash

    def compare_hash(self, file: str, save_path: str) -> bool:
        hash_data = os.path.join(save_path, "hash.sha1")

        current_hash = self.hash_file(file)
        if os.path.exists(hash_data):
            with open(hash_data, "r") as f:
                saved_hash = f.read()
            if current_hash == saved_hash:
                return True
        return False
