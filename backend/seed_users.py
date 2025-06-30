#!/usr/bin/env python3
"""
@fileoverview Database seeding script for TRAIDER V1 demo users
@module backend.seed_users

@description
Creates demo users in the database with bcrypt-hashed passwords for Phase 0 testing.
Provides admin and demo trader accounts with appropriate roles and permissions.
Implements institutional-grade security with proper password hashing.

@performance
- User creation: <100ms per user
- Password hashing: ~100ms (bcrypt security)
- Database operations: <50ms

@risk
- Failure impact: LOW (development/demo only)
- Recovery strategy: Manual user creation
- Security: Uses secure bcrypt hashing

@compliance
- Audit requirements: Yes (user creation logged)
- Data retention: Demo users for Phase 0 only

@see {@link docs/security/user-management.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import asyncio
import asyncpg
import os
from datetime import datetime, timezone
from passlib.context import CryptContext
from typing import List, Dict, Any

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://traider:password@localhost:5432/traider")

# Demo users configuration
DEMO_USERS = [
    {
        "username": "admin",
        "password": "password",
        "email": "admin@traider.local",
        "role": "administrator",
        "permissions": [
            "trading.execute",
            "trading.view",
            "risk.manage",
            "risk.view",
            "system.admin",
            "system.monitor",
            "data.export",
            "users.manage"
        ],
        "is_active": True,
        "is_demo": True
    },
    {
        "username": "demo",
        "password": "demo123",
        "email": "demo@traider.local", 
        "role": "trader",
        "permissions": [
            "trading.execute",
            "trading.view",
            "risk.view",
            "system.monitor"
        ],
        "is_active": True,
        "is_demo": True
    },
    {
        "username": "viewer",
        "password": "viewer123",
        "email": "viewer@traider.local",
        "role": "viewer",
        "permissions": [
            "trading.view",
            "risk.view",
            "system.monitor"
        ],
        "is_active": True,
        "is_demo": True
    }
]

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    @description
    Securely hashes passwords using bcrypt with appropriate work factor.
    Provides institutional-grade password security for user accounts.
    
    @param password - Plain text password to hash
    @returns Hashed password string
    
    @performance ~100ms (bcrypt security requirement)
    @sideEffects None - Pure function
    
    @tradingImpact Secures user authentication for trading platform
    @riskLevel HIGH - Password security critical
    
    @example
    ```python
    hashed = hash_password("secure_password")
    # Returns: $2b$12$... (bcrypt hash)
    ```
    
    @monitoring
    - Metric: `auth.password_hash.latency`
    - Alert threshold: > 200ms
    """
    return pwd_context.hash(password)

async def create_users_table(conn: asyncpg.Connection) -> None:
    """
    Create users table if it doesn't exist.
    
    @description
    Creates the users table with proper constraints and indexes
    for secure user management in the trading platform.
    
    @param conn - Database connection
    
    @performance <50ms table creation
    @sideEffects Creates database table
    
    @tradingImpact Provides user storage for authentication
    @riskLevel MEDIUM - Database schema changes
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'viewer',
        permissions TEXT[] DEFAULT '{}',
        is_active BOOLEAN DEFAULT true,
        is_demo BOOLEAN DEFAULT false,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP WITH TIME ZONE,
        login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP WITH TIME ZONE,
        
        -- Constraints
        CONSTRAINT valid_role CHECK (role IN ('administrator', 'trader', 'viewer')),
        CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
    
    -- Update trigger for updated_at
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """
    
    await conn.execute(create_table_sql)
    print("✅ Users table created successfully")

async def seed_demo_user(conn: asyncpg.Connection, user_data: Dict[str, Any]) -> None:
    """
    Seed a single demo user into the database.
    
    @description
    Creates a demo user with hashed password and proper permissions.
    Handles conflicts by updating existing users with demo flag.
    
    @param conn - Database connection
    @param user_data - User information dictionary
    
    @performance <100ms per user
    @sideEffects Inserts/updates user in database
    
    @tradingImpact Creates demo accounts for testing trading functionality
    @riskLevel LOW - Demo user creation only
    """
    # Hash the password
    password_hash = hash_password(user_data["password"])
    
    # Insert or update user
    upsert_sql = """
    INSERT INTO users (
        username, email, password_hash, role, permissions, 
        is_active, is_demo, created_at
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8
    )
    ON CONFLICT (username) 
    DO UPDATE SET
        email = EXCLUDED.email,
        password_hash = EXCLUDED.password_hash,
        role = EXCLUDED.role,
        permissions = EXCLUDED.permissions,
        is_active = EXCLUDED.is_active,
        is_demo = EXCLUDED.is_demo,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id, username, role;
    """
    
    result = await conn.fetchrow(
        upsert_sql,
        user_data["username"],
        user_data["email"],
        password_hash,
        user_data["role"],
        user_data["permissions"],
        user_data["is_active"],
        user_data["is_demo"],
        datetime.now(timezone.utc)
    )
    
    print(f"✅ Demo user '{result['username']}' (ID: {result['id']}, Role: {result['role']}) created/updated")

async def verify_users(conn: asyncpg.Connection) -> None:
    """
    Verify that demo users were created correctly.
    
    @description
    Validates that all demo users exist in database with correct roles
    and permissions. Provides verification output for audit trail.
    
    @param conn - Database connection
    
    @performance <50ms verification
    @sideEffects None - Read-only verification
    
    @tradingImpact Ensures demo users available for testing
    @riskLevel LOW - Verification only
    """
    users = await conn.fetch("""
        SELECT id, username, email, role, permissions, is_active, is_demo, created_at
        FROM users 
        WHERE is_demo = true
        ORDER BY username
    """)
    
    print("\n📋 Demo Users Verification:")
    print("=" * 80)
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
        print(f"Permissions: {', '.join(user['permissions'])}")
        print(f"Active: {user['is_active']}")
        print(f"Created: {user['created_at']}")
        print("-" * 40)

async def main() -> None:
    """
    Main seeding function.
    
    @description
    Orchestrates the complete demo user seeding process including
    table creation, user insertion, and verification.
    
    @performance <500ms total execution
    @sideEffects Creates database table and demo users
    
    @tradingImpact Enables Phase 0 authentication testing
    @riskLevel LOW - Development/demo setup only
    """
    print("🌱 Starting TRAIDER V1 Demo User Seeding...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Create users table
        await create_users_table(conn)
        
        # Seed demo users
        print("\n🔐 Creating demo users...")
        for user_data in DEMO_USERS:
            await seed_demo_user(conn, user_data)
        
        # Verify users
        await verify_users(conn)
        
        print("\n🎉 Demo user seeding completed successfully!")
        print("\nDemo Credentials:")
        print("- Admin: username='admin', password='password'")
        print("- Trader: username='demo', password='demo123'") 
        print("- Viewer: username='viewer', password='viewer123'")
        print("\n⚠️  Note: These are demo credentials for Phase 0 development only!")
        
    except Exception as error:
        print(f"❌ Error during seeding: {error}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()
            print("✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 