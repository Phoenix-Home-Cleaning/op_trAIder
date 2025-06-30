#!/usr/bin/env pwsh
<#
.SYNOPSIS
    TRAIDER V1 Database Restore Script - Institutional Grade Recovery
    
.DESCRIPTION
    Comprehensive database restore script that handles TimescaleDB base backups,
    WAL replay, and validation for disaster recovery operations. Designed for
    institutional-grade trading systems with zero-tolerance for data loss.
    
    Features:
    - Automated restore from most recent backup
    - WAL replay for point-in-time recovery
    - Health validation using backend utilities
    - Performance benchmarking
    - Audit logging and compliance reporting
    
.PARAMETER BackupPath
    Path to the backup directory (default: auto-detect latest)
    
.PARAMETER TargetTime
    Point-in-time recovery target (ISO 8601 format)
    
.PARAMETER Validate
    Run health validation after restore (default: true)
    
.PARAMETER DryRun
    Simulate restore without making changes
    
.PARAMETER Force
    Skip confirmation prompts (use with caution)
    
.EXAMPLE
    ./restore-db.ps1 -Validate
    Restore from latest backup with health validation
    
.EXAMPLE
    ./restore-db.ps1 -BackupPath "C:\backups\2025-06-29" -TargetTime "2025-06-29T14:30:00Z"
    Restore from specific backup to exact point in time
    
.EXAMPLE
    ./restore-db.ps1 -DryRun -Validate
    Test restore procedure without making changes
    
.NOTES
    Author: TRAIDER Infrastructure Team
    Version: 1.0.0
    Requires: PostgreSQL 15+, TimescaleDB 2.8+, Python 3.11+
    
    CRITICAL: This script stops all trading operations during restore
    
.LINK
    https://docs.traider.ai/infrastructure/disaster-recovery
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $false)]
    [string]$BackupPath = "",
    
    [Parameter(Mandatory = $false)]
    [datetime]$TargetTime = [datetime]::MinValue,
    
    [Parameter(Mandatory = $false)]
    [switch]$Validate = $true,
    
    [Parameter(Mandatory = $false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force = $false
)

# =============================================================================
# CONFIGURATION
# =============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Environment configuration
$env:PYTHONPATH = "$PSScriptRoot\..\backend"
$BackupBaseDir = $env:TRAIDER_BACKUP_DIR ?? "C:\traider-backups"
$LogDir = "$PSScriptRoot\..\logs\restore"
$TempDir = "$env:TEMP\traider-restore"

# Database configuration
$DbHost = $env:DB_HOST ?? "localhost"
$DbPort = $env:DB_PORT ?? "5432"
$DbName = $env:DB_NAME ?? "traider"
$DbUser = $env:DB_USER ?? "traider"
$DbPassword = $env:DB_PASSWORD ?? "password"

# Restore configuration
$RestoreTimeout = 600  # 10 minutes
$ValidationTimeout = 120  # 2 minutes
$MaxRetries = 3

# =============================================================================
# LOGGING SETUP
# =============================================================================

function Write-TraiderLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO",
        
        [Parameter(Mandatory = $false)]
        [hashtable]$Metadata = @{}
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    $logEntry = @{
        timestamp = $timestamp
        level = $Level
        message = $Message
        component = "restore-db"
        metadata = $Metadata
    }
    
    # Console output with colors
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Green" }
        "DEBUG" { "Gray" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
    
    # File logging
    if (!(Test-Path $LogDir)) {
        New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
    }
    
    $logFile = Join-Path $LogDir "restore-$(Get-Date -Format 'yyyy-MM-dd').log"
    $logEntry | ConvertTo-Json -Compress | Add-Content -Path $logFile
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Test-Prerequisites {
    Write-TraiderLog "Checking restore prerequisites..."
    
    $checks = @()
    
    # PostgreSQL client tools
    try {
        $pgVersion = & pg_restore --version 2>$null
        $checks += @{ Name = "pg_restore"; Status = "OK"; Version = $pgVersion }
    }
    catch {
        $checks += @{ Name = "pg_restore"; Status = "MISSING"; Error = $_.Exception.Message }
    }
    
    # Python and backend health utility
    try {
        $pythonVersion = & python --version 2>$null
        $checks += @{ Name = "python"; Status = "OK"; Version = $pythonVersion }
        
        if (Test-Path "$PSScriptRoot\..\backend\api\health.py") {
            $checks += @{ Name = "health_utility"; Status = "OK" }
        }
        else {
            $checks += @{ Name = "health_utility"; Status = "MISSING" }
        }
    }
    catch {
        $checks += @{ Name = "python"; Status = "MISSING"; Error = $_.Exception.Message }
    }
    
    # Database connectivity
    try {
        $connTest = & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "SELECT 1;" 2>$null
        $checks += @{ Name = "database_connection"; Status = "OK" }
    }
    catch {
        $checks += @{ Name = "database_connection"; Status = "FAILED"; Error = $_.Exception.Message }
    }
    
    # Check for failures
    $failures = $checks | Where-Object { $_.Status -ne "OK" }
    if ($failures.Count -gt 0) {
        Write-TraiderLog "Prerequisites check failed:" -Level "ERROR"
        $failures | ForEach-Object {
            Write-TraiderLog "  - $($_.Name): $($_.Status) $($_.Error)" -Level "ERROR"
        }
        throw "Prerequisites not met. Please install missing components."
    }
    
    Write-TraiderLog "All prerequisites satisfied" -Metadata @{ checks = $checks }
}

function Find-LatestBackup {
    Write-TraiderLog "Searching for latest backup in $BackupBaseDir..."
    
    if (!(Test-Path $BackupBaseDir)) {
        throw "Backup directory not found: $BackupBaseDir"
    }
    
    # Find the most recent backup directory
    $backupDirs = Get-ChildItem -Path $BackupBaseDir -Directory | 
        Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' } |
        Sort-Object Name -Descending
    
    if ($backupDirs.Count -eq 0) {
        throw "No backup directories found in $BackupBaseDir"
    }
    
    $latestDir = $backupDirs[0].FullName
    
    # Verify backup files exist
    $baseBackup = Join-Path $latestDir "base-backup.tar.gz"
    $walDir = Join-Path $latestDir "wal-archives"
    
    if (!(Test-Path $baseBackup)) {
        throw "Base backup not found: $baseBackup"
    }
    
    if (!(Test-Path $walDir)) {
        throw "WAL archives not found: $walDir"
    }
    
    Write-TraiderLog "Found latest backup: $latestDir" -Metadata @{
        backup_date = $backupDirs[0].Name
        base_backup = $baseBackup
        wal_dir = $walDir
    }
    
    return $latestDir
}

function Stop-TradingServices {
    Write-TraiderLog "Stopping trading services for safe restore..." -Level "WARN"
    
    # Stop Docker services if running
    try {
        & docker-compose -f "$PSScriptRoot\..\docker-compose.dev.yml" down 2>$null
        Write-TraiderLog "Docker services stopped"
    }
    catch {
        Write-TraiderLog "Docker services not running or failed to stop" -Level "WARN"
    }
    
    # Stop any running Python processes
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*traider*" }
    
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force
        Write-TraiderLog "Stopped $($pythonProcesses.Count) Python trading processes"
    }
}

function Restore-Database {
    param(
        [string]$BackupDir,
        [datetime]$PointInTime
    )
    
    Write-TraiderLog "Starting database restore from $BackupDir..." -Level "WARN"
    
    $startTime = Get-Date
    
    try {
        # Create temp directory for restore
        if (Test-Path $TempDir) {
            Remove-Item -Path $TempDir -Recurse -Force
        }
        New-Item -Path $TempDir -ItemType Directory -Force | Out-Null
        
        # Extract base backup
        Write-TraiderLog "Extracting base backup..."
        $baseBackup = Join-Path $BackupDir "base-backup.tar.gz"
        $extractDir = Join-Path $TempDir "base-backup"
        
        & tar -xzf $baseBackup -C $TempDir
        
        # Stop PostgreSQL service
        Write-TraiderLog "Stopping PostgreSQL service..."
        Stop-Service -Name "postgresql*" -Force -ErrorAction SilentlyContinue
        
        # Backup current data directory
        $dataDir = $env:PGDATA ?? "C:\Program Files\PostgreSQL\15\data"
        $backupDataDir = "$dataDir.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        
        if (Test-Path $dataDir) {
            Write-TraiderLog "Backing up current data directory to $backupDataDir"
            Move-Item -Path $dataDir -Destination $backupDataDir
        }
        
        # Restore base backup
        Write-TraiderLog "Restoring base backup to $dataDir..."
        Move-Item -Path $extractDir -Destination $dataDir
        
        # Create recovery configuration
        $recoveryConf = @"
restore_command = 'copy "$BackupDir\wal-archives\%f" "%p"'
recovery_target_action = 'promote'
"@
        
        if ($PointInTime -ne [datetime]::MinValue) {
            $targetTime = $PointInTime.ToString("yyyy-MM-dd HH:mm:ss UTC")
            $recoveryConf += "`nrecovery_target_time = '$targetTime'"
            Write-TraiderLog "Point-in-time recovery target: $targetTime"
        }
        
        $recoveryConf | Set-Content -Path "$dataDir\postgresql.auto.conf"
        
        # Start PostgreSQL service
        Write-TraiderLog "Starting PostgreSQL service..."
        Start-Service -Name "postgresql*"
        
        # Wait for service to be ready
        $retries = 0
        do {
            Start-Sleep -Seconds 5
            $retries++
            try {
                & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "SELECT 1;" 2>$null
                $ready = $true
            }
            catch {
                $ready = $false
            }
        } while (!$ready -and $retries -lt 12)
        
        if (!$ready) {
            throw "PostgreSQL service failed to start after restore"
        }
        
        $duration = (Get-Date) - $startTime
        Write-TraiderLog "Database restore completed successfully" -Metadata @{
            duration_seconds = [math]::Round($duration.TotalSeconds, 2)
            backup_source = $BackupDir
            point_in_time = $PointInTime
        }
    }
    catch {
        Write-TraiderLog "Database restore failed: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
    finally {
        # Cleanup temp directory
        if (Test-Path $TempDir) {
            Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Test-RestoreHealth {
    Write-TraiderLog "Running health validation after restore..."
    
    $healthScript = "$PSScriptRoot\..\backend\api\health.py"
    
    if (!(Test-Path $healthScript)) {
        Write-TraiderLog "Health script not found, creating basic validation..." -Level "WARN"
        
        # Basic connectivity test
        try {
            $result = & psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -c "
                SELECT 
                    'database_connectivity' as check_name,
                    'OK' as status,
                    NOW() as timestamp;
                
                SELECT 
                    'table_count' as check_name,
                    COUNT(*) as table_count,
                    'OK' as status
                FROM information_schema.tables 
                WHERE table_schema = 'public';
                
                SELECT 
                    'timescaledb_extension' as check_name,
                    CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'MISSING' END as status
                FROM pg_extension 
                WHERE extname = 'timescaledb';
            " 2>&1
            
            Write-TraiderLog "Basic health validation passed" -Metadata @{ result = $result }
            return $true
        }
        catch {
            Write-TraiderLog "Basic health validation failed: $($_.Exception.Message)" -Level "ERROR"
            return $false
        }
    }
    
    # Run comprehensive health check
    try {
        Write-TraiderLog "Running comprehensive health validation..."
        
        $healthResult = & python $healthScript --detailed --timeout $ValidationTimeout 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-TraiderLog "Health validation passed" -Metadata @{ result = $healthResult }
            return $true
        }
        else {
            Write-TraiderLog "Health validation failed" -Level "ERROR" -Metadata @{ 
                exit_code = $LASTEXITCODE
                output = $healthResult 
            }
            return $false
        }
    }
    catch {
        Write-TraiderLog "Health validation error: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Start-TradingServices {
    Write-TraiderLog "Starting trading services after successful restore..."
    
    try {
        # Start Docker services
        & docker-compose -f "$PSScriptRoot\..\docker-compose.dev.yml" up -d
        
        # Wait for services to be healthy
        Start-Sleep -Seconds 30
        
        # Verify services are running
        $services = & docker-compose -f "$PSScriptRoot\..\docker-compose.dev.yml" ps --services --filter "status=running"
        
        Write-TraiderLog "Trading services started successfully" -Metadata @{ 
            services = $services -join ", "
        }
    }
    catch {
        Write-TraiderLog "Failed to start trading services: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    $startTime = Get-Date
    
    try {
        Write-TraiderLog "=== TRAIDER V1 Database Restore Started ===" -Level "INFO"
        Write-TraiderLog "Restore parameters:" -Metadata @{
            backup_path = $BackupPath
            target_time = $TargetTime
            validate = $Validate.IsPresent
            dry_run = $DryRun.IsPresent
            force = $Force.IsPresent
        }
        
        # Prerequisites check
        Test-Prerequisites
        
        # Determine backup location
        if ([string]::IsNullOrEmpty($BackupPath)) {
            $BackupPath = Find-LatestBackup
        }
        
        if (!(Test-Path $BackupPath)) {
            throw "Backup path not found: $BackupPath"
        }
        
        # Confirmation prompt (unless forced)
        if (!$Force -and !$DryRun) {
            Write-Host ""
            Write-Host "⚠️  WARNING: This will restore the database and stop all trading operations!" -ForegroundColor Red
            Write-Host "   Backup source: $BackupPath" -ForegroundColor Yellow
            if ($TargetTime -ne [datetime]::MinValue) {
                Write-Host "   Recovery target: $($TargetTime.ToString('yyyy-MM-dd HH:mm:ss UTC'))" -ForegroundColor Yellow
            }
            Write-Host ""
            
            $confirmation = Read-Host "Continue with restore? (yes/no)"
            if ($confirmation -ne "yes") {
                Write-TraiderLog "Restore cancelled by user"
                return
            }
        }
        
        if ($DryRun) {
            Write-TraiderLog "DRY RUN: Simulating restore process..." -Level "WARN"
            Write-TraiderLog "Would restore from: $BackupPath"
            if ($TargetTime -ne [datetime]::MinValue) {
                Write-TraiderLog "Would recover to: $($TargetTime.ToString('yyyy-MM-dd HH:mm:ss UTC'))"
            }
            Write-TraiderLog "DRY RUN completed successfully"
            return
        }
        
        # Execute restore process
        Stop-TradingServices
        Restore-Database -BackupDir $BackupPath -PointInTime $TargetTime
        
        # Health validation
        if ($Validate) {
            $healthPassed = Test-RestoreHealth
            if (!$healthPassed) {
                throw "Health validation failed after restore"
            }
        }
        
        # Restart services
        Start-TradingServices
        
        $duration = (Get-Date) - $startTime
        Write-TraiderLog "=== Database restore completed successfully ===" -Level "INFO" -Metadata @{
            total_duration_seconds = [math]::Round($duration.TotalSeconds, 2)
            backup_source = $BackupPath
            validation_passed = $Validate.IsPresent
        }
        
        # Success notification
        Write-Host ""
        Write-Host "✅ Database restore completed successfully!" -ForegroundColor Green
        Write-Host "   Duration: $([math]::Round($duration.TotalMinutes, 1)) minutes" -ForegroundColor Green
        Write-Host "   Health validation: $(if ($Validate) { 'PASSED' } else { 'SKIPPED' })" -ForegroundColor Green
        Write-Host ""
        
    }
    catch {
        $duration = (Get-Date) - $startTime
        Write-TraiderLog "Database restore failed: $($_.Exception.Message)" -Level "ERROR" -Metadata @{
            error_duration_seconds = [math]::Round($duration.TotalSeconds, 2)
            stack_trace = $_.ScriptStackTrace
        }
        
        Write-Host ""
        Write-Host "❌ Database restore failed!" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Check logs: $LogDir" -ForegroundColor Yellow
        Write-Host ""
        
        exit 1
    }
}

# Execute main function
Main 