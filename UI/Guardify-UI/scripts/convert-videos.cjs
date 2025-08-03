const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const inputDir = path.join(__dirname, '../public/videos');
const outputDir = path.join(inputDir, 'fixed');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

fs.readdirSync(inputDir).forEach(file => {
  const ext = path.extname(file).toLowerCase();
  const baseName = path.basename(file, ext);

  if (['.mp4', '.avi', '.mov', '.mkv', '.webm'].includes(ext)) {
    const inputPath = path.join(inputDir, file);
    const outputPath = path.join(outputDir, `${baseName}.mp4`);

    console.log(`🎞️  Converting: ${file} → ${baseName}.mp4`);
    try {
      execSync(`ffmpeg -i "${inputPath}" -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k -movflags +faststart "${outputPath}"`, { stdio: 'inherit' });
    } catch (err) {
      console.error(`Failed to convert ${file}`, err.message);
    }
  }
});
