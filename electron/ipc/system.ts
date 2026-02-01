import { ipcMain } from 'electron';
import os from 'os';
import { shell } from 'electron';

export function setupSystemIPC() {
  // 获取系统信息
  ipcMain.handle('system:info', async () => {
    return {
      platform: os.platform(),
      arch: os.arch(),
      version: os.release(),
      memory: os.totalmem(),
      cpus: os.cpus().length,
    };
  });

  // 打开外部链接
  ipcMain.handle('system:openExternal', async (_, url: string) => {
    try {
      await shell.openExternal(url);
    } catch (error) {
      console.error('Open external error:', error);
      throw error;
    }
  });
}
