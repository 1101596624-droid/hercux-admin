import { ipcMain, dialog, BrowserWindow } from 'electron';
import fs from 'fs/promises';

export function setupFileIPC() {
  // 选择文件
  ipcMain.handle('dialog:selectFile', async () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] },
      ],
    });
    return result.canceled ? null : result.filePaths[0];
  });

  // 选择文件夹
  ipcMain.handle('dialog:selectFolder', async () => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory'],
    });
    return result.canceled ? null : result.filePaths[0];
  });

  // 保存文件
  ipcMain.handle('file:save', async (_: Electron.IpcMainInvokeEvent, data: any) => {
    const mainWindow = BrowserWindow.getAllWindows()[0];
    const result = await dialog.showSaveDialog(mainWindow, {
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'Excel Files', extensions: ['xlsx'] },
      ],
    });

    if (!result.canceled && result.filePath) {
      try {
        const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        await fs.writeFile(result.filePath, content, 'utf-8');
        return true;
      } catch (error) {
        console.error('File save error:', error);
        return false;
      }
    }
    return false;
  });

  // 读取文件
  ipcMain.handle('file:read', async (_, filePath: string) => {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return content;
    } catch (error) {
      console.error('File read error:', error);
      throw error;
    }
  });
}
