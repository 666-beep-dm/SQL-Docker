"""
Password hashing and verification using bcrypt directly.

Why not passlib?
----------------
passlib 1.7.4 (the last release, from 2020) has a known incompatibility
with bcrypt >= 4.x where it passes an incorrect byte representation to
the bcrypt C extension, causing a ``ValueError: password cannot be longer
than 72 bytes`` even for short passwords. Since passlib is unmaintained,
the fix is to use bcrypt directly — it is simpler, actively maintained,
and is already a transitive dependency anyway.

72-byte limit
-------------
bcrypt truncates input at 72 bytes by design (the cipher block size).
We enforce a 72-byte UTF-8 limit at the schema layer (max_length=72 on
the password field) so the silent truncation never silently drops chars.
"""
import bcrypt


def hash_password(plain: str) -> str:
    """
    Return a bcrypt hash of ``plain``.

    Parameters
    ----------
    plain:
        The raw plaintext password string.

    Returns
    -------
    str
        A bcrypt hash string (e.g. ``$2b$12$...``).
    """
    password_bytes = plain.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Return True if ``plain`` matches the stored ``hashed`` value.

    Parameters
    ----------
    plain:
        The raw plaintext password to check.
    hashed:
        The stored bcrypt hash string.
    """
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))