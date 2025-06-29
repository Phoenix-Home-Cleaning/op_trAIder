#!/usr/bin/env pwsh

Write-Host "TRAIDER V1 - Creating Secure Environment File" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to generate secure random string
function New-SecureString {
    param([int]$Length = 32)
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $result = [System.Convert]::ToBase64String($bytes) -replace '[/+=]', ''
    $rng.Dispose()
    return $result.Substring(0, [Math]::Min($Length, $result.Length))
}

# Function to generate secure password
function New-SecurePassword {
    param([int]$Length = 24)
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    
    for ($i = 0; $i -lt $Length; $i++) {
        $bytes = New-Object byte[] 1
        $rng.GetBytes($bytes)
        $password += $chars[$bytes[0] % $chars.Length]
    }
    
    $rng.Dispose()
    return $password
}

Write-Host "Generating cryptographically secure secrets..." -ForegroundColor Green

# Generate all secrets
$secrets = @{
    "SECRET_KEY" = New-SecureString -Length 64
    "JWT_SECRET_KEY" = New-SecureString -Length 64
    "DASHBOARD_PASSWORD" = New-SecurePassword -Length 24
    "GUEST_PASSWORD" = New-SecurePassword -Length 16
    "DB_PASSWORD" = New-SecureString -Length 24
    "POSTGRES_PASSWORD" = New-SecureString -Length 24
    "REDIS_PASSWORD" = New-SecureString -Length 20
    "BINANCE_API_KEY" = "traider_" + (New-SecureString -Length 32).ToLower()
    "BINANCE_SECRET_KEY" = New-SecureString -Length 64
    "COINBASE_API_KEY" = "traider_" + (New-SecureString -Length 32).ToLower()
    "COINBASE_SECRET_KEY" = New-SecureString -Length 64
    "COINBASE_PASSPHRASE" = New-SecurePassword -Length 16
    "TRADING_ENCRYPTION_KEY" = New-SecureString -Length 64
    "RISK_MANAGEMENT_KEY" = New-SecureString -Length 48
    "SESSION_SECRET" = New-SecureString -Length 64
    "CACHE_ENCRYPTION_KEY" = New-SecureString -Length 48
}

Write-Host "Generated $($secrets.Count) secure secrets" -ForegroundColor Green

# Read the template
$template = Get-Content "backend/env.example" -Raw

# Create the header
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
$header = @"
# =============================================================================
# TRAIDER V1 - GENERATED ENVIRONMENT CONFIGURATION
# =============================================================================
# Environment: development
# Generated: $timestamp
# Security Level: INSTITUTIONAL GRADE (256-bit cryptographic secrets)
# 
# CRITICAL SECURITY NOTICE:
# - These secrets are cryptographically secure and unique
# - NEVER commit this file to version control
# - Store securely and rotate regularly
# =============================================================================

"@

# Replace placeholders in template
$envContent = $template
foreach ($key in $secrets.Keys) {
    $pattern = "$key=.*"
    $replacement = "$key=$($secrets[$key])"
    $envContent = $envContent -replace $pattern, $replacement
}

# Set development-specific values
$envContent = $envContent -replace "ENVIRONMENT=.*", "ENVIRONMENT=development"
$envContent = $envContent -replace "DEBUG=.*", "DEBUG=true"
$envContent = $envContent -replace "RELOAD=.*", "RELOAD=true"
$envContent = $envContent -replace "PAPER_TRADING=.*", "PAPER_TRADING=true"
$envContent = $envContent -replace "LOG_LEVEL=.*", "LOG_LEVEL=DEBUG"

# Combine header and content
$finalContent = $header + $envContent

# Write to file
$finalContent | Out-File -FilePath "backend/.env" -Encoding UTF8

Write-Host "Environment file created: backend/.env" -ForegroundColor Green
Write-Host ""
Write-Host "SECURITY SUMMARY:" -ForegroundColor Yellow
Write-Host "- JWT Secrets: 256-bit cryptographic strength" -ForegroundColor White
Write-Host "- Passwords: Mixed character sets with high entropy" -ForegroundColor White
Write-Host "- API Keys: Unique secure identifiers" -ForegroundColor White
Write-Host "- All secrets generated with cryptographic RNG" -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Start development: docker-compose -f docker-compose.dev.yml up" -ForegroundColor White
Write-Host "2. Run tests: npm run test" -ForegroundColor White
Write-Host "3. Replace exchange API keys with real credentials when ready" -ForegroundColor White
Write-Host ""
Write-Host "Ready for world-class testing!" -ForegroundColor Green 