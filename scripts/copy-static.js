const fs = require('fs');
const path = require('path');

function copyDir(src, dest) {
  if (!fs.existsSync(src)) {
    console.log(`Source not found: ${src}`);
    return;
  }

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

const projectRoot = path.join(__dirname, '..');
const standaloneDir = path.join(projectRoot, '.next/standalone');

// Copy static files
const staticSrc = path.join(projectRoot, '.next/static');
const staticDest = path.join(standaloneDir, '.next/static');
console.log('Copying static files...');
copyDir(staticSrc, staticDest);

// Copy public folder
const publicSrc = path.join(projectRoot, 'public');
const publicDest = path.join(standaloneDir, 'public');
console.log('Copying public files...');
copyDir(publicSrc, publicDest);

console.log('Done!');
