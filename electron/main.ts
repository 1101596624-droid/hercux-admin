import { app, BrowserWindow, ipcMain, session, Menu, clipboard } from 'electron';
import path from 'path';
import { spawn, ChildProcess, fork } from 'child_process';
import { setupMenu } from './menu';
import { setupTray } from './tray';
import { setupUpdater } from './updater';
import { setupIPC } from './ipc';

let mainWindow: BrowserWindow | null = null;
let nextServer: ChildProcess | null = null;

const PORT = 23001;

// 获取应用根目录（兼容开发和打包环境）
function getAppRoot(): string {
  if (app.isPackaged) {
    // 打包后，由于 asar: false，资源直接在 resources 目录下
    // 检查多个可能的路径
    const possiblePaths = [
      path.join(process.resourcesPath, 'app'),
      process.resourcesPath,
      path.dirname(app.getPath('exe')),
    ];

    for (const p of possiblePaths) {
      const serverPath = path.join(p, '.next/standalone/server.js');
      console.log('[Electron] Checking path:', serverPath);
      if (require('fs').existsSync(serverPath)) {
        console.log('[Electron] Found server at:', p);
        return p;
      }
    }

    // 默认返回第一个路径
    return possiblePaths[0];
  } else {
    // 开发环境
    return path.join(__dirname, '..');
  }
}

async function startNextServer(): Promise<void> {
  return new Promise((resolve, reject) => {
    const appRoot = getAppRoot();
    const serverPath = path.join(appRoot, '.next/standalone/server.js');
    const serverCwd = path.join(appRoot, '.next/standalone');

    console.log('[Electron] App root:', appRoot);
    console.log('[Electron] Server path:', serverPath);
    console.log('[Electron] Server cwd:', serverCwd);

    // 检查服务器文件是否存在
    const fs = require('fs');
    if (!fs.existsSync(serverPath)) {
      console.error('[Electron] Server file not found:', serverPath);
      console.error('[Electron] Directory contents:', fs.readdirSync(appRoot));
      reject(new Error(`Server file not found: ${serverPath}`));
      return;
    }

    // 使用 fork 启动 standalone 服务器
    nextServer = fork(serverPath, [], {
      cwd: serverCwd,
      env: {
        ...process.env,
        NODE_ENV: 'production',
        PORT: PORT.toString(),
        HOSTNAME: 'localhost',
      },
      stdio: ['ignore', 'pipe', 'pipe', 'ipc'],
    });

    nextServer.stdout?.on('data', (data) => {
      const output = data.toString();
      console.log('[Next.js]', output);
      if (output.includes('Ready') || output.includes('started') || output.includes('Listening')) {
        resolve();
      }
    });

    nextServer.stderr?.on('data', (data) => {
      console.error('[Next.js Error]', data.toString());
    });

    nextServer.on('error', (err) => {
      console.error('Failed to start Next.js server:', err);
      reject(err);
    });

    // 超时后也继续
    setTimeout(() => resolve(), 3000);
  });
}

function createWindow() {
  const appRoot = getAppRoot();

  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 1400,
    minHeight: 800,
    title: 'HERCU 管理后台',
    icon: path.join(appRoot, 'public/icons/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      spellcheck: false,
      webSecurity: false,  // 允许跨域请求（Electron 本地应用）
    },
    backgroundColor: '#0F172A',
    show: false,
  });

  // 开发环境加载 Next.js dev server
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3001');
  } else {
    // 生产环境加载内置服务器
    mainWindow.loadURL(`http://localhost:${PORT}`);
  }

  // 始终打开开发者工具（固定在右侧）
  mainWindow.webContents.openDevTools({ mode: 'right' });

  // 窗口加载完成后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // 窗口关闭处理
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // 右键菜单 - 复制/粘贴功能
  mainWindow.webContents.on('context-menu', (event, params) => {
    const menuTemplate: Electron.MenuItemConstructorOptions[] = [];

    // 如果有选中文本，显示复制选项
    if (params.selectionText) {
      menuTemplate.push({
        label: '复制',
        role: 'copy',
      });
    }

    // 如果是可编辑区域，显示粘贴选项
    if (params.isEditable) {
      menuTemplate.push({
        label: '粘贴',
        role: 'paste',
      });
      menuTemplate.push({
        label: '剪切',
        role: 'cut',
      });
      menuTemplate.push({
        label: '全选',
        role: 'selectAll',
      });
    }

    if (menuTemplate.length > 0) {
      const contextMenu = Menu.buildFromTemplate(menuTemplate);
      contextMenu.popup();
    }
  });

  // 设置内容安全策略
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'",
          "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
          "style-src 'self' 'unsafe-inline' blob:",
          "img-src 'self' data: blob: http: https: http://106.14.180.66:8001 http://localhost:*",
          "connect-src 'self' http://localhost:* http://106.14.180.66:* https://106.14.180.66:* https://api.hercu.com https://*.aipor.cc https://*.hiapi.online ws://localhost:*",
          "font-src 'self' data:",
          "media-src 'self' http://106.14.180.66:8001 blob:",
        ].join('; '),
      },
    });
  });
}

// 应用启动
app.whenReady().then(async () => {
  // 生产环境启动 Next.js 服务器
  if (process.env.NODE_ENV !== 'development') {
    try {
      await startNextServer();
    } catch (err) {
      console.error('Failed to start Next.js server:', err);
    }
  }

  createWindow();
  setupMenu();
  setupTray(mainWindow);
  setupUpdater();
  setupIPC();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 所有窗口关闭时退出（macOS 除外）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 应用退出时关闭 Next.js 服务器并清除 token
app.on('before-quit', async () => {
  // 清除 localStorage 中的 token
  if (mainWindow && !mainWindow.isDestroyed()) {
    try {
      await mainWindow.webContents.executeJavaScript(`
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      `);
    } catch (e) {
      console.log('[Electron] Failed to clear token:', e);
    }
  }

  if (nextServer) {
    nextServer.kill();
    nextServer = null;
  }
});

// 导出主窗口引用供其他模块使用
export { mainWindow };
