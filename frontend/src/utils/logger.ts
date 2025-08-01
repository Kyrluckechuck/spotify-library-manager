/**
 * Centralized logging utility for the application
 * This utility provides a consistent interface for logging while respecting ESLint rules
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerOptions {
  level?: LogLevel;
  prefix?: string;
}

class Logger {
  private level: LogLevel;
  private prefix: string;

  constructor(options: LoggerOptions = {}) {
    this.level = options.level || 'info';
    this.prefix = options.prefix || '';
  }

  private shouldLog(messageLevel: LogLevel): boolean {
    const levels: Record<LogLevel, number> = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3,
    };
    return levels[messageLevel] >= levels[this.level];
  }

  private formatMessage(level: LogLevel, message: string): string {
    const timestamp = new Date().toISOString();
    const prefix = this.prefix ? `[${this.prefix}] ` : '';
    return `${prefix}[${level.toUpperCase()}] ${timestamp}: ${message}`;
  }

  debug(message: string, ...args: unknown[]): void {
    if (this.shouldLog('debug')) {
      // eslint-disable-next-line no-console
      console.log(this.formatMessage('debug', message), ...args);
    }
  }

  info(message: string, ...args: unknown[]): void {
    if (this.shouldLog('info')) {
      // eslint-disable-next-line no-console
      console.log(this.formatMessage('info', message), ...args);
    }
  }

  warn(message: string, ...args: unknown[]): void {
    if (this.shouldLog('warn')) {
      // eslint-disable-next-line no-console
      console.warn(this.formatMessage('warn', message), ...args);
    }
  }

  error(message: string, ...args: unknown[]): void {
    if (this.shouldLog('error')) {
      // eslint-disable-next-line no-console
      console.error(this.formatMessage('error', message), ...args);
    }
  }

  // Special methods for test output with emojis
  test(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(message, ...args);
  }

  success(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(`✅ ${message}`, ...args);
  }

  failure(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(`❌ ${message}`, ...args);
  }

  section(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(`📋 ${message}`, ...args);
  }

  action(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(`🔍 ${message}`, ...args);
  }

  summary(message: string, ...args: unknown[]): void {
    // eslint-disable-next-line no-console
    console.log(`📊 ${message}`, ...args);
  }
}

// Create default logger instances
export const logger = new Logger();
export const testLogger = new Logger({ prefix: 'TEST' });

// Factory function to create loggers with specific prefixes
export const createLogger = (
  prefix: string,
  options?: LoggerOptions
): Logger => {
  return new Logger({ ...options, prefix });
};

// Export the Logger class for custom instances
export { Logger };
