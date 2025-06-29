-- =============================================================================
-- TRAIDER V1 - TimescaleDB Initialization Script
-- =============================================================================
--
-- This script runs automatically when the PostgreSQL container starts.
-- It sets up TimescaleDB extension and basic configuration for the
-- TRAIDER trading platform.
--
-- Performance: Optimized for time-series data ingestion and querying
-- Risk: CRITICAL - Database foundation for all trading operations
-- Compliance: All schema changes logged and tracked
--
-- See: docs/architecture/database-setup.md
-- Author: TRAIDER Team
-- Since: 1.0.0-alpha

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Set timezone to UTC for consistent time handling
SET timezone = 'UTC';

-- Configure TimescaleDB settings for trading workloads
ALTER SYSTEM SET timescaledb.max_background_workers = 8;
ALTER SYSTEM SET shared_preload_libraries = 'timescaledb';

-- Create additional extensions for trading functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query performance monitoring
CREATE EXTENSION IF NOT EXISTS "btree_gin";     -- Improved indexing for JSON queries

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'TRAIDER V1: TimescaleDB initialization completed successfully';
    RAISE NOTICE 'TRAIDER V1: Database ready for trading operations';
END $$; 