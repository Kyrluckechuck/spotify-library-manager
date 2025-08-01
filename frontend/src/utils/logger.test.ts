import { describe, it, expect, vi } from 'vitest';
import { Logger, createLogger } from './logger';

describe('Logger', () => {
  it('should create a logger instance', () => {
    const logger = new Logger();
    expect(logger).toBeInstanceOf(Logger);
  });

  it('should create a logger with prefix', () => {
    const logger = createLogger('TEST');
    expect(logger).toBeInstanceOf(Logger);
  });

  it('should log messages with different levels', () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(vi.fn());
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(vi.fn());
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(vi.fn());
    const logger = new Logger({ level: 'debug' }); // Set to debug level to include all messages

    logger.info('Test info message');
    logger.debug('Test debug message');
    logger.warn('Test warn message');
    logger.error('Test error message');

    expect(logSpy).toHaveBeenCalledTimes(2); // info, debug
    expect(warnSpy).toHaveBeenCalledTimes(1); // warn
    expect(errorSpy).toHaveBeenCalledTimes(1); // error

    logSpy.mockRestore();
    warnSpy.mockRestore();
    errorSpy.mockRestore();
  });

  it('should respect log level filtering', () => {
    const logSpy = vi.spyOn(console, 'log').mockImplementation(vi.fn());
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(vi.fn());
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(vi.fn());
    const logger = new Logger({ level: 'warn' });

    logger.info('This should not be logged');
    logger.debug('This should not be logged');
    logger.warn('This should be logged');
    logger.error('This should be logged');

    expect(logSpy).toHaveBeenCalledTimes(0);
    expect(warnSpy).toHaveBeenCalledTimes(1);
    expect(errorSpy).toHaveBeenCalledTimes(1);

    logSpy.mockRestore();
    warnSpy.mockRestore();
    errorSpy.mockRestore();
  });

  it('should format messages with timestamps', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(vi.fn());
    const logger = new Logger();

    logger.info('Test message');

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringMatching(
        /\[INFO\] \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: Test message/
      )
    );
    consoleSpy.mockRestore();
  });

  it('should include prefix in formatted messages', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(vi.fn());
    const logger = new Logger({ prefix: 'TEST' });

    logger.info('Test message');

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringMatching(
        /\[TEST\] \[INFO\] \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z: Test message/
      )
    );
    consoleSpy.mockRestore();
  });
});
