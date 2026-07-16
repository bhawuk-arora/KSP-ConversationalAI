// frontend/rename_assets.js
const fs = require("fs");
const path = require("path");

const outDir = path.join(__dirname, "out");
const nextDir = path.join(outDir, "_next");
const targetDir = path.join(outDir, "next");

// 1. Rename _next to next
if (fs.existsSync(nextDir)) {
  if (fs.existsSync(targetDir)) {
    fs.rmSync(targetDir, { recursive: true, force: true });
  }
  fs.renameSync(nextDir, targetDir);
  console.log("Renamed _next to next in out folder!");
} else {
  console.log("_next folder not found or already renamed.");
}

// 2. Recursively replace paths in files
function replaceInFiles(dir) {
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      replaceInFiles(filePath);
    } else if (stat.isFile() && /\.(html|js|css|json|txt)$/.test(file)) {
      try {
        let content = fs.readFileSync(filePath, "utf8");
        const updated = content.replace(/\/_next\//g, "/next/").replace(/_next\//g, "next/");
        
        if (updated !== content) {
          fs.writeFileSync(filePath, updated, "utf8");
          console.log(`Updated paths in: ${file}`);
        }
      } catch (e) {
        console.error(`Error processing ${file}: ${e}`);
      }
    }
  });
}

replaceInFiles(outDir);
