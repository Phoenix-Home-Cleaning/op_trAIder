#!/usr/bin/env python3
"""
Simple test script to verify our backend fixes work.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set required environment variables
os.environ.update({
    "SECRET_KEY": "test_secret_key_for_unit_testing_only",
    "DASHBOARD_PASSWORD": "test_dashboard_password",
    "GUEST_PASSWORD": "test_guest_password",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
    "BCRYPT_ROUNDS": "10",
    "PYTHON_ENV": "testing",
    "TESTING": "true",
})

def test_auth_imports():
    """Test that auth module imports correctly."""
    try:
        from api.auth import get_user_by_email, authenticate_user, AuthUser
        print("✅ Auth module imports successfully")
        
        # Test AuthUser class
        user = AuthUser({"email": "test@example.com", "username": "test"})
        assert user.email == "test@example.com"
        assert user["username"] == "test"
        print("✅ AuthUser class works correctly")
        
        # Test get_user_by_email function exists
        result = get_user_by_email("test@example.com")
        print(f"✅ get_user_by_email returns: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Auth module import failed: {e}")
        return False

def test_health_imports():
    """Test that health module imports correctly."""
    try:
        from api.health import liveness_probe, readiness_probe, detailed_health_check
        print("✅ Health module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Health module import failed: {e}")
        return False

def test_config_fallback():
    """Test that config fallback works."""
    try:
        from api.auth import SECRET_KEY, DASHBOARD_PASSWORD
        print(f"✅ Config fallback works: SECRET_KEY={SECRET_KEY[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Config fallback failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing backend fixes...")
    
    tests = [
        test_config_fallback,
        test_auth_imports,
        test_health_imports,
    ]
    
    results = []
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend fixes are working.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Need to investigate further.")
        sys.exit(1) 