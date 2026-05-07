import pytest
from datetime import timedelta
from backend.infra.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token
)

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_access_token_creation_and_decoding():
    subject = "user123"
    token = create_access_token(subject)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == subject
    assert decoded["type"] == "access"

def test_refresh_token_creation_and_decoding():
    subject = "user123"
    token = create_refresh_token(subject)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == subject
    assert decoded["type"] == "refresh"

def test_token_expiration():
    subject = "user123"
    # Create a token that is already expired
    token = create_access_token(subject, expires_delta=timedelta(seconds=-1))
    decoded = decode_token(token)
    assert decoded is None

def test_invalid_token():
    assert decode_token("invalid.token.here") is None
