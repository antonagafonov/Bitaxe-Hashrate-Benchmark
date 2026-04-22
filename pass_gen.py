#!/usr/bin/env python3
"""
Generate a secure password containing upper, lower, digits and symbols.
Defaults to 12 characters and guarantees at least one char from each class.
"""

import secrets
import string
import argparse


def generate_password(length: int = 12) -> str:
    if length < 4:
        raise ValueError("length must be at least 4 to include all character classes")

    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    # Guarantee one character from each required class
    mandatory = [
        secrets.choice(lowers),
        secrets.choice(uppers),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]

    # Fill the rest from the full pool
    pool = lowers + uppers + digits + symbols
    remainder = [secrets.choice(pool) for _ in range(length - len(mandatory))]

    # Shuffle securely
    password_list = mandatory + remainder
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a secure password.")
    parser.add_argument(
        "--length", type=int, default=12, help="Password length (default: 12)"
    )
    args = parser.parse_args()

    print(generate_password(args.length))
