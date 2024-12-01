from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generowanie klucza prywatnego
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Zapisz klucz prywatny do pliku
with open("private_key.pem", "wb") as private_key_file:
    private_key_file.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

# Generowanie klucza publicznego
public_key = private_key.public_key()

# Zapisz klucz publiczny do pliku
with open("public_key.pem", "wb") as public_key_file:
    public_key_file.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
