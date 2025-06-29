#!/usr/bin/env tsx

/**
 * @fileoverview Script to create new Architecture Decision Records (ADRs)
 * 
 * Automates the creation of ADR documents with proper numbering and templating.
 * Ensures consistent format and helps track architectural decisions over time.
 * 
 * @author TRAIDER Team
 * @since 2025-06-29
 */

import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';
import { execSync } from 'child_process';

interface ADRConfig {
  title: string;
  status: 'Proposed' | 'Accepted' | 'Deprecated' | 'Superseded';
  deciders: string[];
  technicalStory?: string;
}

class ADRGenerator {
  private projectRoot: string;
  private adrDir: string;

  constructor() {
    this.projectRoot = process.cwd();
    this.adrDir = join(this.projectRoot, 'docs/adr');
  }

  /**
   * Create a new ADR with proper numbering
   */
  async createADR(config: ADRConfig): Promise<string> {
    const nextNumber = this.getNextADRNumber();
    const filename = this.generateFilename(nextNumber, config.title);
    const content = this.generateADRContent(nextNumber, config);
    
    const filepath = join(this.adrDir, filename);
    writeFileSync(filepath, content, 'utf-8');
    
    console.log(`✅ Created ADR: ${filename}`);
    console.log(`📄 Path: ${filepath}`);
    
    return filepath;
  }

  /**
   * List all existing ADRs
   */
  listADRs(): void {
    if (!existsSync(this.adrDir)) {
      console.log('No ADRs found. Create your first ADR!');
      return;
    }

    const files = readdirSync(this.adrDir)
      .filter(f => f.endsWith('.md'))
      .sort();

    console.log('📚 Existing ADRs:');
    files.forEach(file => {
      const content = readFileSync(join(this.adrDir, file), 'utf-8');
      const title = this.extractTitle(content);
      const status = this.extractStatus(content);
      
      console.log(`  ${file.replace('.md', '')}: ${title} [${status}]`);
    });
  }

  /**
   * Get the next ADR number
   */
  private getNextADRNumber(): number {
    if (!existsSync(this.adrDir)) {
      return 1;
    }

    const files = readdirSync(this.adrDir)
      .filter(f => f.match(/^adr-\d{3}-/))
      .map(f => parseInt(f.match(/^adr-(\d{3})-/)?.[1] || '0'))
      .sort((a, b) => b - a);

    return files.length > 0 ? files[0] + 1 : 1;
  }

  /**
   * Generate filename for ADR
   */
  private generateFilename(number: number, title: string): string {
    const slug = title
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '-')
      .substring(0, 50);
    
    return `adr-${number.toString().padStart(3, '0')}-${slug}.md`;
  }

  /**
   * Generate ADR content from template
   */
  private generateADRContent(number: number, config: ADRConfig): string {
    const template = readFileSync(join(this.adrDir, 'template.md'), 'utf-8');
    const date = new Date().toISOString().split('T')[0];
    
    return template
      .replace(/ADR-XXX/g, `ADR-${number.toString().padStart(3, '0')}`)
      .replace(/\[Title\]/g, config.title)
      .replace(/\[Proposed \| Accepted \| Deprecated \| Superseded\]/g, config.status)
      .replace(/YYYY-MM-DD/g, date)
      .replace(/\[List of decision makers\]/g, config.deciders.join(', '))
      .replace(/\[Link to issue\/story if applicable\]/g, config.technicalStory || 'N/A');
  }

  /**
   * Extract title from ADR content
   */
  private extractTitle(content: string): string {
    const match = content.match(/^# ADR-\d{3}: (.+)$/m);
    return match ? match[1] : 'Unknown Title';
  }

  /**
   * Extract status from ADR content
   */
  private extractStatus(content: string): string {
    const match = content.match(/\*\*Status\*\*: (.+)$/m);
    return match ? match[1] : 'Unknown Status';
  }
}

// CLI Interface
/**
 * Main CLI interface for ADR generation
 *
 * @description
 * Command-line interface for creating and managing Architecture Decision Records.
 * Supports creating new ADRs with proper numbering, listing existing ADRs,
 * and providing help information. Integrates with VS Code for editing.
 *
 * @returns {Promise<void>} Promise that resolves when CLI operation completes
 *
 * @throws {Error} If ADR creation or file operations fail
 *
 * @performance
 * - Execution time: <5s for ADR creation
 * - Memory usage: <50MB
 * - File I/O operations for ADR management
 *
 * @sideEffects
 * - Creates new ADR files in docs/adr/ directory
 * - Reads existing ADR files for numbering
 * - May launch VS Code editor
 * - Exits process on errors
 *
 * @tradingImpact Enables architectural decision tracking for trading platform
 * @riskLevel LOW - Documentation utility
 *
 * @example
 * ```bash
 * # Create new ADR
 * tsx scripts/create-adr.ts new "Use Redis for Caching"
 * 
 * # List existing ADRs
 * tsx scripts/create-adr.ts list
 * ```
 *
 * @monitoring
 * - Metric: `adr.creation.count`
 * - Alert threshold: N/A (utility script)
 */
async function main() {
  const args = process.argv.slice(2);
  const generator = new ADRGenerator();

  if (args.length === 0 || args[0] === '--help') {
    console.log(`
📚 TRAIDER ADR Generator

Usage:
  tsx scripts/create-adr.ts [command] [options]

Commands:
  new <title>     Create a new ADR
  list           List all existing ADRs
  help           Show this help message

Examples:
  tsx scripts/create-adr.ts new "Use TypeScript for Frontend"
  tsx scripts/create-adr.ts list
`);
    return;
  }

  const command = args[0];

  switch (command) {
    case 'new':
      const title = args.slice(1).join(' ');
      if (!title) {
        console.error('❌ Please provide a title for the ADR');
        process.exit(1);
      }

      const config: ADRConfig = {
        title,
        status: 'Proposed',
        deciders: ['TRAIDER Team'],
        technicalStory: undefined
      };

      const filepath = await generator.createADR(config);
      
      // Open in editor if available
      try {
        execSync(`code "${filepath}"`, { stdio: 'ignore' });
      } catch {
        console.log('💡 Tip: Open the file in your editor to complete the ADR');
      }
      break;

    case 'list':
      generator.listADRs();
      break;

    default:
      console.error(`❌ Unknown command: ${command}`);
      console.log('Use --help for usage information');
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { ADRGenerator, ADRConfig }; 