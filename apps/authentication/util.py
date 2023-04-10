# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import hashlib

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/
SALT_DEFAULT = "kelompok7"

def hash_pass(password):
    """Hash a password for storing."""

    salted_password = (password + SALT_DEFAULT).encode()
    pwdhash = hashlib.sha256(salted_password).hexdigest()

    return pwdhash


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    salted_password = (provided_password + SALT_DEFAULT).encode()
    computed_hash   = hashlib.sha256(salted_password).hexdigest()


    return computed_hash == stored_password
