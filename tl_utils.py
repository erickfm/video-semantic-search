#!/usr/bin/env python3
"""
tl_utils.py
===========
Tiny helper utilities for TwelveLabs integration.
Handles API key loading and client creation.
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from twelvelabs import TwelveLabs


def load_api_key() -> str:
    """
    Load TwelveLabs API key from environment.
    
    Returns:
        str: The API key
        
    Raises:
        SystemExit: If API key is not found
    """
    load_dotenv()
    api_key = os.getenv("TWELVE_LABS_API_KEY")
    if not api_key:
        sys.exit(
            "❌ TWELVE_LABS_API_KEY not found. "
            "Add it to .env or export it as an environment variable."
        )
    return api_key


def build_client(api_key: Optional[str] = None) -> TwelveLabs:
    """
    Build and return a TwelveLabs client.
    
    Args:
        api_key: Optional API key. If not provided, loads from environment.
        
    Returns:
        TwelveLabs: Configured client instance
    """
    if api_key is None:
        api_key = load_api_key()
    
    return TwelveLabs(api_key=api_key)


def get_client() -> TwelveLabs:
    """
    Convenience function to get a TwelveLabs client with error handling.
    
    Returns:
        TwelveLabs: Configured client instance
    """
    try:
        return build_client()
    except Exception as exc:
        sys.exit(f"❌ Failed to create TwelveLabs client: {exc!r}") 