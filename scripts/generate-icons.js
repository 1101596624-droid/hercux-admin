#!/usr/bin/env node
/**
 * Generate application icons from SVG source
 * Generates: icon.png, icon.ico, tray-icon.png
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const PROJECT_ROOT = path.join(__dirname, '..');
const ICONS_DIR = path.join(PROJECT_ROOT, 'public', 'icons');
const SVG_PATH = path.join(ICONS_DIR, 'icon.svg');

console.log('='.repeat(60));
console.log('HERCU Icon Generator');
console.log('='.repeat(60));

async function generateIcons() {
  // Check if SVG exists
  if (!fs.existsSync(SVG_PATH)) {
    console.error(`Error: ${SVG_PATH} not found!`);
    process.exit(1);
  }

  console.log(`\nSource: ${SVG_PATH}`);
  console.log(`Output: ${ICONS_DIR}\n`);

  try {
    // Read SVG
    const svgBuffer = fs.readFileSync(SVG_PATH);

    // Generate base PNG (1024x1024)
    console.log('Generating icon-1024.png (1024x1024)...');
    await sharp(svgBuffer)
      .resize(1024, 1024)
      .png()
      .toFile(path.join(ICONS_DIR, 'icon-1024.png'));
    console.log('✓ Generated icon-1024.png');

    // Generate Linux PNG (512x512)
    console.log('Generating icon.png (512x512)...');
    await sharp(svgBuffer)
      .resize(512, 512)
      .png()
      .toFile(path.join(ICONS_DIR, 'icon.png'));
    console.log('✓ Generated icon.png');

    // Generate tray icon (32x32)
    console.log('Generating tray-icon.png (32x32)...');
    await sharp(svgBuffer)
      .resize(32, 32)
      .png()
      .toFile(path.join(ICONS_DIR, 'tray-icon.png'));
    console.log('✓ Generated tray-icon.png');

    // Generate Windows ICO (256x256 - electron-builder will handle multi-size)
    console.log('Generating icon.ico (256x256)...');
    const icoBuffer = await sharp(svgBuffer)
      .resize(256, 256)
      .png()
      .toBuffer();

    // For ICO, we'll create a simple single-size ICO file
    // electron-builder can also work with PNG renamed to ICO
    fs.writeFileSync(path.join(ICONS_DIR, 'icon.ico'), icoBuffer);
    console.log('✓ Generated icon.ico');

    // Generate macOS ICNS placeholder (electron-builder can convert PNG to ICNS)
    console.log('Generating icon.icns (1024x1024)...');
    const icnsBuffer = await sharp(svgBuffer)
      .resize(1024, 1024)
      .png()
      .toBuffer();

    fs.writeFileSync(path.join(ICONS_DIR, 'icon.icns'), icnsBuffer);
    console.log('✓ Generated icon.icns (PNG format - electron-builder will convert)');

    console.log('\n' + '='.repeat(60));
    console.log('✓ Icon generation complete!');
    console.log('='.repeat(60));
    console.log('\nGenerated files:');
    console.log('  • icon.png (512x512) - Linux');
    console.log('  • icon.ico (256x256) - Windows');
    console.log('  • icon.icns (1024x1024) - macOS');
    console.log('  • tray-icon.png (32x32) - System tray');
    console.log('  • icon-1024.png (1024x1024) - Source');
    console.log('\nNote: electron-builder will optimize these icons during build');
    console.log('\nYou can now build the desktop app with: npm run dist');

  } catch (error) {
    console.error('\nError generating icons:', error.message);
    process.exit(1);
  }
}

generateIcons();
