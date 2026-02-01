import { Menu } from 'electron';

export function setupMenu() {
  // 隐藏菜单栏
  Menu.setApplicationMenu(null);
}
