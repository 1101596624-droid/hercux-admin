import { ipcMain } from 'electron';
import { setupFileIPC } from './file';
import { setupDatabaseIPC } from './database';
import { setupSystemIPC } from './system';
import { setupWindowIPC } from './window';
import { setupAppIPC } from './app';

export function setupIPC() {
  setupFileIPC();
  setupDatabaseIPC();
  setupSystemIPC();
  setupWindowIPC();
  setupAppIPC();
}
