#!/usr/bin/env pwsh
<#
.SYNOPSIS
    TRAIDER V1 - World-Class Testing Infrastructure Setup

.DESCRIPTION
    Sets up comprehensive testing infrastructure for institutional-grade
    cryptocurrency trading platform including unit, integration, performance,
    security, and chaos engineering tests.

.NOTES
    Author: TRAIDER Team
    Version: 1.0.0
    Testing Standards: INSTITUTIONAL GRADE
#>

Write-Host "🧪 TRAIDER V1 - World-Class Testing Infrastructure Setup" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Validate environment
if (-not (Test-Path "package.json")) {
    Write-Error "❌ package.json not found. Run from project root directory."
    exit 1
}

Write-Host "📦 Installing testing dependencies..." -ForegroundColor Green

# Install comprehensive testing stack
$testDependencies = @(
    # Core Testing Framework
    "@testing-library/react@^14.0.0",
    "@testing-library/jest-dom@^6.1.0",
    "@testing-library/user-event@^14.5.0",
    
    # Performance & Load Testing
    "k6@^0.46.0",
    "autocannon@^7.15.0",
    
    # Security Testing
    "jest-security@^1.0.0",
    "audit-ci@^6.6.1",
    
    # API Testing
    "supertest@^6.3.3",
    "nock@^13.3.8",
    
    # Database Testing
    "jest-environment-node@^29.7.0",
    "@types/supertest@^2.0.16",
    
    # Mocking & Fixtures
    "msw@^2.0.0",
    "factory-bot@^1.2.0",
    
    # Coverage & Reporting
    "nyc@^15.1.0",
    "jest-html-reporters@^3.1.5"
)

npm install --save-dev $($testDependencies -join " ")

Write-Host "✅ Testing dependencies installed" -ForegroundColor Green
Write-Host "🏗️  Setting up test infrastructure..." -ForegroundColor Yellow

# Create test directories
$testDirs = @(
    "tests/unit/frontend",
    "tests/unit/backend", 
    "tests/integration",
    "tests/e2e",
    "tests/performance",
    "tests/security",
    "tests/fixtures",
    "tests/mocks",
    "tests/utils"
)

foreach ($dir in $testDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created $dir" -ForegroundColor White
    }
}

Write-Host "🎯 Test infrastructure ready for implementation" -ForegroundColor Green
Write-Host "📋 Next: Run .\scripts\generate-secrets.ps1 to create secure environment" -ForegroundColor Yellow 