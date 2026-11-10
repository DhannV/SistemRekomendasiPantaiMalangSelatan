
from getpass import getpass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from security import hash_password


def create_admin():
    print("=== PEMBUATAN AKUN ADMIN ===")

    username = input("Masukkan username Admin: ").strip()

    if len(username) < 3 or len(username) > 50:
        print("Username harus terdiri dari 3–50 karakter.")
        return

    if not all(c.isalnum() or c == "_" for c in username):
        print("Username hanya boleh berisi huruf, angka, dan underscore (_).")
        return

    password = getpass("Masukkan password Admin: ")
    confirm_password = getpass("Konfirmasi password: ")

    if len(password) < 8 or len(password) > 128:
        print("Password harus terdiri dari 8–128 karakter.")
        return

    if password != confirm_password:
        print("Konfirmasi password tidak cocok.")
        return

    try:
        with engine.begin() as connection:
            existing_admin = connection.execute(
                text("""
                    SELECT id
                    FROM public.users
                    WHERE username = :username
                """),
                {"username": username},
            ).first()

            if existing_admin:
                print("Username sudah terdaftar.")
                return

            hashed_password = hash_password(password)

            result = connection.execute(
                text("""
                    INSERT INTO public.users
                        (username, hashed_password, role)
                    VALUES
                        (:username, :hashed_password, 'admin')
                    RETURNING id, username, role, created_at
                """),
                {
                    "username": username,
                    "hashed_password": hashed_password,
                },
            )

            admin = result.mappings().one()

        print("\nAkun Admin berhasil dibuat!")
        print(f"ID       : {admin['id']}")
        print(f"Username : {admin['username']}")
        print(f"Role     : {admin['role']}")
        print(f"Dibuat   : {admin['created_at']}")

    except SQLAlchemyError as error:
        print(f"Gagal membuat akun Admin: {error}")


if __name__ == "__main__":
    create_admin()
