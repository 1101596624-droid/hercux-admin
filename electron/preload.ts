import { contextBridge, ipcRenderer } from 'electron';

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 文件操作
  selectFile: () => ipcRenderer.invoke('dialog:selectFile'),
  selectFolder: () => ipcRenderer.invoke('dialog:selectFolder'),
  saveFile: (data: any) => ipcRenderer.invoke('file:save', data),
  readFile: (path: string) => ipcRenderer.invoke('file:read', path),

  // 数据库操作
  queryDatabase: (sql: string) => ipcRenderer.invoke('db:query', sql),

  // 系统操作
  getSystemInfo: () => ipcRenderer.invoke('system:info'),
  openExternal: (url: string) => ipcRenderer.invoke('system:openExternal', url),

  // 应用操作
  getAppVersion: () => ipcRenderer.invoke('app:version'),
  checkForUpdates: () => ipcRenderer.invoke('app:checkUpdates'),

  // 窗口操作
  minimizeWindow: () => ipcRenderer.invoke('window:minimize'),
  maximizeWindow: () => ipcRenderer.invoke('window:maximize'),
  closeWindow: () => ipcRenderer.invoke('window:close'),

  // 事件监听
  onUpdateAvailable: (callback: Function) => {
    ipcRenderer.on('update-available', (_, info) => callback(info));
  },
  onUpdateDownloaded: (callback: Function) => {
    ipcRenderer.on('update-downloaded', (_, info) => callback(info));
  },
  removeUpdateListeners: () => {
    ipcRenderer.removeAllListeners('update-available');
    ipcRenderer.removeAllListeners('update-downloaded');
  },
});

// TypeScript 类型定义
declare global {
  interface Window {
    electronAPI: {
      selectFile: () => Promise<string | null>;
      selectFolder: () => Promise<string | null>;
      saveFile: (data: any) => Promise<boolean>;
      readFile: (path: string) => Promise<string>;
      queryDatabase: (sql: string) => Promise<any[]>;
      getSystemInfo: () => Promise<SystemInfo>;
      openExternal: (url: string) => Promise<void>;
      getAppVersion: () => Promise<string>;
      checkForUpdates: () => Promise<void>;
      minimizeWindow: () => Promise<void>;
      maximizeWindow: () => Promise<void>;
      closeWindow: () => Promise<void>;
      onUpdateAvailable: (callback: Function) => void;
      onUpdateDownloaded: (callback: Function) => void;
      removeUpdateListeners: () => void;
    };
  }

  interface SystemInfo {
    platform: string;
    arch: string;
    version: string;
    memory: number;
    cpus: number;
  }
}

export {};
