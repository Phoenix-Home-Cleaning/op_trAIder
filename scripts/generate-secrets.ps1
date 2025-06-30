#!/usr/bin/env pwsh
<#
.SYNOPSIS
    TRAIDER V1 - Cryptographically Secure Secret Generation Script

.DESCRIPTION
    Generates all required cryptographically secure passwords, API keys, and secrets
    for the TRAIDER V1 institutional trading platform. Creates production-ready
    .env files with proper security standards.

.PARAMETER Environment
    Target environment: development, staging, production

.PARAMETER OutputPath
    Path to output the .env file (default: .env)

.EXAMPLE
    .\scripts\generate-secrets.ps1 -Environment development
    .\scripts\generate-secrets.ps1 -Environment production -OutputPath .env.prod

.NOTES
    Author: TRAIDER Team
    Version: 1.0.0
    Security Level: INSTITUTIONAL GRADE
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ".env"
)

# =============================================================================
# SECURITY FUNCTIONS
# =============================================================================

function New-CryptographicSecret {
    <#
    .SYNOPSIS
        Generates cryptographically secure random bytes
    .PARAMETER Length
        Length in bytes (default: 32 for 256-bit security)
    .PARAMETER Format
        Output format: hex, base64, alphanumeric
    #>
    param(
        [int]$Length = 32,
        [ValidateSet("hex", "base64", "alphanumeric")]
        [string]$Format = "hex"
    )
    
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    
    switch ($Format) {
        "hex" { 
            return [System.BitConverter]::ToString($bytes) -replace '-', '' 
        }
        "base64" { 
            return [System.Convert]::ToBase64String($bytes) -replace '[/+=]', ''
        }
        "alphanumeric" {
            $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            $result = ""
            foreach ($byte in $bytes) {
                $result += $chars[$byte % $chars.Length]
            }
            return $result
        }
    }
}

function New-SecurePassword {
    <#
    .SYNOPSIS
        Generates secure password with mixed character sets
    .PARAMETER Length
        Password length (minimum 16 for institutional security)
    #>
    param([int]$Length = 24)
    
    if ($Length -lt 16) {
        throw "Password length must be at least 16 characters for institutional security"
    }
    
    $uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    $lowercase = "abcdefghijklmnopqrstuvwxyz"
    $numbers = "0123456789"
    $symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    $allChars = $uppercase + $lowercase + $numbers + $symbols
    
    $password = ""
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    
    # Ensure at least one character from each set
    $password += Get-RandomChar $uppercase $rng
    $password += Get-RandomChar $lowercase $rng
    $password += Get-RandomChar $numbers $rng
    $password += Get-RandomChar $symbols $rng
    
    # Fill remaining length
    for ($i = 4; $i -lt $Length; $i++) {
        $password += Get-RandomChar $allChars $rng
    }
    
    $rng.Dispose()
    
    # Shuffle the password
    $passwordArray = $password.ToCharArray()
    for ($i = $passwordArray.Length - 1; $i -gt 0; $i--) {
        $j = Get-Random -Maximum ($i + 1)
        $temp = $passwordArray[$i]
        $passwordArray[$i] = $passwordArray[$j]
        $passwordArray[$j] = $temp
    }
    
    return -join $passwordArray
}

function Get-RandomChar {
    param([string]$CharSet, [System.Security.Cryptography.RandomNumberGenerator]$Rng)
    
    $bytes = New-Object byte[] 1
    $Rng.GetBytes($bytes)
    return $CharSet[$bytes[0] % $CharSet.Length]
}

function New-JWTSecret {
    <#
    .SYNOPSIS
        Generates JWT-compatible secret (256-bit minimum)
    #>
    return New-CryptographicSecret -Length 32 -Format "base64"
}

function New-DatabasePassword {
    <#
    .SYNOPSIS
        Generates database-safe password (no special chars that might cause issues)
    #>
    param([int]$Length = 32)
    
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return New-CryptographicSecret -Length $Length -Format "alphanumeric"
}

function New-APIKey {
    <#
    .SYNOPSIS
        Generates API key in standard format
    #>
    $prefix = "placeholder_api_key_"
    $key = New-CryptographicSecret -Length 24 -Format "alphanumeric"
    return $prefix + $key.ToLower()
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

Write-Host "TRAIDER V1 - Cryptographically Secure Secret Generation" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Output Path: $OutputPath" -ForegroundColor Yellow
Write-Host ""

# Validate environment
if (-not (Test-Path ".env.example")) {
    Write-Error ".env.example not found. Run from project root directory."
    exit 1
}

# Create output directory if it doesn't exist
$outputDir = Split-Path $OutputPath -Parent
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Generating cryptographically secure secrets..." -ForegroundColor Green

# =============================================================================
# GENERATE ALL SECRETS
# =============================================================================

$secrets = @{}

# JWT & Authentication Secrets (CRITICAL)
Write-Host "  -> JWT & Authentication secrets..." -ForegroundColor White
$secrets["SECRET_KEY"] = New-JWTSecret
$secrets["JWT_SECRET_KEY"] = New-JWTSecret
$secrets["DASHBOARD_PASSWORD"] = New-SecurePassword -Length 24
$secrets["GUEST_PASSWORD"] = New-SecurePassword -Length 16

# Database Secrets
Write-Host "  -> Database credentials..." -ForegroundColor White
$secrets["DB_PASSWORD"] = New-DatabasePassword -Length 24
$secrets["POSTGRES_PASSWORD"] = $secrets["DB_PASSWORD"]

# Redis Secrets
Write-Host "  -> Redis credentials..." -ForegroundColor White
$secrets["REDIS_PASSWORD"] = New-DatabasePassword -Length 20

# Exchange API Keys (Placeholders - Replace with real keys)
Write-Host "  -> Exchange API placeholders..." -ForegroundColor White
$secrets["BINANCE_API_KEY"] = New-APIKey
$secrets["BINANCE_SECRET_KEY"] = New-CryptographicSecret -Length 32 -Format "base64"
$secrets["COINBASE_API_KEY"] = New-APIKey
$secrets["COINBASE_SECRET_KEY"] = New-CryptographicSecret -Length 32 -Format "base64"
$secrets["COINBASE_PASSPHRASE"] = New-SecurePassword -Length 16

# Monitoring & Observability
Write-Host "  -> Monitoring secrets..." -ForegroundColor White
$secrets["SENTRY_DSN"] = "https://placeholder@sentry.io/project-id"

# Trading Security
Write-Host "  -> Trading security keys..." -ForegroundColor White
$secrets["TRADING_ENCRYPTION_KEY"] = New-CryptographicSecret -Length 32 -Format "hex"
$secrets["RISK_MANAGEMENT_KEY"] = New-CryptographicSecret -Length 24 -Format "base64"

# Session & Cache
Write-Host "  -> Session management..." -ForegroundColor White
$secrets["SESSION_SECRET"] = New-CryptographicSecret -Length 32 -Format "base64"
$secrets["CACHE_ENCRYPTION_KEY"] = New-CryptographicSecret -Length 24 -Format "hex"

Write-Host ""
Write-Host "Generated $(($secrets.Keys).Count) cryptographically secure secrets" -ForegroundColor Green

# =============================================================================
# CREATE .ENV FILE
# =============================================================================

Write-Host "Creating .env file..." -ForegroundColor Green

# Read template
$template = Get-Content ".env.example" -Raw

# Environment-specific configurations
$envConfigs = @{
    "development" = @{
        "ENVIRONMENT" = "development"
        "DEBUG" = "true"
        "RELOAD" = "true"
        "PAPER_TRADING" = "true"
        "BINANCE_TESTNET" = "true"
        "COINBASE_SANDBOX" = "true"
        "LOG_LEVEL" = "DEBUG"
        "CORS_ORIGINS" = "http://localhost:3000,http://localhost:8000"
    }
    "staging" = @{
        "ENVIRONMENT" = "staging"
        "DEBUG" = "false"
        "RELOAD" = "false"
        "PAPER_TRADING" = "true"
        "BINANCE_TESTNET" = "true"
        "COINBASE_SANDBOX" = "true"
        "LOG_LEVEL" = "INFO"
        "CORS_ORIGINS" = "https://staging.traider.com"
    }
    "production" = @{
        "ENVIRONMENT" = "production"
        "DEBUG" = "false"
        "RELOAD" = "false"
        "PAPER_TRADING" = "false"
        "BINANCE_TESTNET" = "false"
        "COINBASE_SANDBOX" = "false"
        "LOG_LEVEL" = "WARNING"
        "CORS_ORIGINS" = "https://traider.com"
    }
}

# Replace placeholders with generated secrets
$envContent = $template
foreach ($key in $secrets.Keys) {
    $placeholder = "$key=.*"
    $replacement = "$key=$($secrets[$key])"
    $envContent = $envContent -replace $placeholder, $replacement
}

# Apply environment-specific configurations
$config = $envConfigs[$Environment]
foreach ($key in $config.Keys) {
    $placeholder = "$key=.*"
    $replacement = "$key=$($config[$key])"
    $envContent = $envContent -replace $placeholder, $replacement
}

# Add generation metadata
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
$header = @"
# =============================================================================
# TRAIDER V1 - GENERATED ENVIRONMENT CONFIGURATION
# =============================================================================
# Environment: $Environment
# Generated: $timestamp
# Generator: scripts/generate-secrets.ps1
# Security Level: INSTITUTIONAL GRADE (256-bit cryptographic secrets)
# 
# ⚠️  CRITICAL SECURITY NOTICE:
# - These secrets are cryptographically secure and unique
# - NEVER commit this file to version control
# - Store securely and rotate regularly
# - Use environment-specific secret management in production
# =============================================================================

"@

$envContent = $header + $envContent

# Write to file
$envContent | Out-File -FilePath $OutputPath -Encoding UTF8

Write-Host "Environment file created: $OutputPath" -ForegroundColor Green

# =============================================================================
# SECURITY SUMMARY
# =============================================================================

Write-Host ""
Write-Host "SECURITY SUMMARY" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "JWT Secrets: 256-bit cryptographic strength" -ForegroundColor Green
Write-Host "Passwords: 16-24 characters with mixed character sets" -ForegroundColor Green
Write-Host "API Keys: Unique identifiers with secure random generation" -ForegroundColor Green
Write-Host "Database: Alphanumeric passwords safe for all DB engines" -ForegroundColor Green
Write-Host "Trading: Dedicated encryption keys for financial operations" -ForegroundColor Green

Write-Host ""
Write-Host "NEXT STEPS" -ForegroundColor Yellow
Write-Host "=============" -ForegroundColor Yellow
Write-Host "1. Review generated .env file for any additional customization" -ForegroundColor White
Write-Host "2. Replace placeholder exchange API keys with real credentials" -ForegroundColor White
Write-Host "3. Set appropriate file permissions: chmod 600 $OutputPath" -ForegroundColor White
Write-Host "4. Start development environment: docker-compose -f docker-compose.dev.yml up" -ForegroundColor White
Write-Host "5. Run tests: npm run test" -ForegroundColor White

Write-Host ""
Write-Host "IMPORTANT REMINDERS" -ForegroundColor Red
Write-Host "======================" -ForegroundColor Red
Write-Host "NEVER commit .env files to version control" -ForegroundColor Red
Write-Host "Use separate .env files for each environment" -ForegroundColor Red
Write-Host "Rotate secrets regularly (every 90 days minimum)" -ForegroundColor Red
Write-Host "Use cloud secret managers in production" -ForegroundColor Red
Write-Host "Monitor for secret exposure in logs and error messages" -ForegroundColor Red

Write-Host ""
Write-Host "Secret generation complete! Ready for world-class testing." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan 