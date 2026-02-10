const fs = require('fs');
const path = require('path');

const sourceDir = 'C:\\Users\\HP\\.gemini\\antigravity\\brain\\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4';
const destDir = 'C:\\Users\\HP\\Downloads\\TechGenie\\src\\assets';

if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
}

const files = [
    { src: 'ai_agent_discovery_1768938373339.png', dest: 'ai_agent_discovery.png' },
    { src: 'instant_generation_1768938393239.png', dest: 'instant_generation.png' },
    { src: 'multi_level_support_1768938414424.png', dest: 'multi_level_support.png' },
    { src: 'fully_customizable_1768938431401.png', dest: 'fully_customizable.png' },
    { src: 'academic_integrity_1768938446903.png', dest: 'academic_integrity.png' },
    { src: 'continuous_updates_1768938462307.png', dest: 'continuous_updates.png' }
];

console.log('Source Dir:', sourceDir);
console.log('Dest Dir:', destDir);

if (fs.existsSync(sourceDir)) {
    console.log('Source dir exists');
    console.log('Source files:', fs.readdirSync(sourceDir));
} else {
    console.error('Source dir does NOT exist');
}

files.forEach(file => {
    const srcPath = path.join(sourceDir, file.src);
    const destPath = path.join(destDir, file.dest);
    try {
        if (fs.existsSync(srcPath)) {
            fs.copyFileSync(srcPath, destPath);
            console.log(`Copied ${file.src} to ${file.dest}`);
        } else {
            console.error(`File not found: ${srcPath}`);
        }
    } catch (err) {
        console.error(`Error copying ${file.src}:`, err);
    }
});
