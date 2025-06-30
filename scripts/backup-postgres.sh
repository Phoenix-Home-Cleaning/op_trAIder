#!/bin/bash

# 🚀 TRAIDER V1 - PostgreSQL Backup Script
# Automated database backup for Docker deployment
# Designed for institutional-grade data protection

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly BACKUP_DIR="/backup"
readonly RETENTION_DAYS=30
readonly DB_HOST="postgres"
readonly DB_PORT="5432"
readonly DB_NAME="traider"
readonly DB_USER="traider"

# Backup file naming
readonly BACKUP_FILE="$BACKUP_DIR/traider_backup_$TIMESTAMP.sql"
readonly COMPRESSED_FILE="$BACKUP_FILE.gz"

# =============================================================================
# LOGGING
# =============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log_info() {
    log "INFO: $*"
}

log_error() {
    log "ERROR: $*"
}

log_success() {
    log "SUCCESS: $*"
}

# =============================================================================
# BACKUP FUNCTIONS
# =============================================================================

create_backup() {
    log_info "Starting PostgreSQL backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Check if PostgreSQL is accessible
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
        log_error "PostgreSQL is not accessible"
        exit 1
    fi
    
    # Create database dump
    log_info "Creating database dump..."
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$BACKUP_FILE.custom"
    
    # Create SQL dump for compatibility
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=plain \
        --file="$BACKUP_FILE"
    
    # Compress SQL dump
    gzip "$BACKUP_FILE"
    
    log_success "Backup created: $COMPRESSED_FILE"
    log_success "Custom backup created: $BACKUP_FILE.custom"
}

verify_backup() {
    log_info "Verifying backup integrity..."
    
    # Check if backup files exist and are not empty
    if [ ! -f "$COMPRESSED_FILE" ] || [ ! -s "$COMPRESSED_FILE" ]; then
        log_error "Compressed backup file is missing or empty"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_FILE.custom" ] || [ ! -s "$BACKUP_FILE.custom" ]; then
        log_error "Custom backup file is missing or empty"
        exit 1
    fi
    
    # Test gzip integrity
    if ! gzip -t "$COMPRESSED_FILE"; then
        log_error "Compressed backup file is corrupted"
        exit 1
    fi
    
    # Test custom format integrity
    if ! pg_restore --list "$BACKUP_FILE.custom" > /dev/null; then
        log_error "Custom backup file is corrupted"
        exit 1
    fi
    
    log_success "Backup verification passed"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Remove old SQL backups
    find "$BACKUP_DIR" -name "traider_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Remove old custom backups
    find "$BACKUP_DIR" -name "traider_backup_*.sql.custom" -type f -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    local backup_count
    backup_count=$(find "$BACKUP_DIR" -name "traider_backup_*.sql.gz" -type f | wc -l)
    
    log_success "Cleanup completed. $backup_count backups retained."
}

generate_backup_report() {
    log_info "Generating backup report..."
    
    local backup_size
    backup_size=$(du -h "$COMPRESSED_FILE" | cut -f1)
    
    local custom_size
    custom_size=$(du -h "$BACKUP_FILE.custom" | cut -f1)
    
    cat > "$BACKUP_DIR/backup_report_$TIMESTAMP.txt" << EOF
TRAIDER V1 Database Backup Report
Generated: $(date)
=====================================

Backup Details:
- Database: $DB_NAME
- Host: $DB_HOST:$DB_PORT
- User: $DB_USER
- Timestamp: $TIMESTAMP

Files Created:
- SQL Dump (compressed): $COMPRESSED_FILE ($backup_size)
- Custom Format: $BACKUP_FILE.custom ($custom_size)

Verification Status: PASSED

Database Statistics:
$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;
" --no-align --field-separator='|')

Backup Process: COMPLETED SUCCESSFULLY
EOF

    log_success "Backup report generated: $BACKUP_DIR/backup_report_$TIMESTAMP.txt"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    log_info "TRAIDER V1 PostgreSQL Backup - Starting"
    log_info "Timestamp: $TIMESTAMP"
    
    # Execute backup process
    create_backup
    verify_backup
    cleanup_old_backups
    generate_backup_report
    
    log_success "Backup process completed successfully!"
    log_info "Backup files:"
    log_info "  - $COMPRESSED_FILE"
    log_info "  - $BACKUP_FILE.custom"
}

# Execute main function
main "$@" 