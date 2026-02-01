import { ipcMain, BrowserWindow } from 'electron';

export function setupWindowIPC() {
  // 最小化窗口
  ipcMain.handle('window:minimize', async () => {
    const window = BrowserWindow.getFocusedWindow();
    if (window) {
      window.minimize();
    }
  });

  // 最大化/还原窗口
  ipcMain.handle('window:maximize', async () => {
    const window = BrowserWindow.getFocusedWindow();
    if (window) {
      if (window.isMaximized()) {
        window.unmaximize();
      } else {
        window.maximize();
      }
    }
  });

  // 关闭窗口
  ipcMain.handle('window:close', async () => {
    const window = BrowserWindow.getFocusedWindow();
    if (window) {
      window.close();
    }
  });
}
