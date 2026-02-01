import { ipcMain, app } from 'electron';

export function setupAppIPC() {
  // 获取应用版本
  ipcMain.handle('app:version', async () => {
    return app.getVersion();
  });

  // 检查更新（将在 updater.ts 中实现）
  ipcMain.handle('app:checkUpdates', async () => {
    // 触发更新检查
    // 实际实现在 updater.ts 中
  });
}
