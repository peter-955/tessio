from abc import ABC, abstractmethod


class SecretCipher(ABC):
    @abstractmethod
    def encrypt(self, plain_text: bytes) -> bytes: ...

    @abstractmethod
    def decrypt(self, cipher_text: bytes) -> bytes: ...
