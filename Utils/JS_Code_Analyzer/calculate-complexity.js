import fs from "fs";
import { fileURLToPath } from 'url';
import path, { dirname } from "path";
import madge from 'madge';
import { ESLint } from "eslint";
import calculateDepths from "./common/calculate-depth.js";

const MADGE_CONFIG = {
  "fileExtensions": ["js", "jsx", "ts", "tsx"]
}

const ESLINT_CONFIG = {
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  extends: ["plugin:@typescript-eslint/recommended"],
  "rules": {
    "complexity": ["error", 0], // Example: Report error if complexity is greater than 5
    "max-lines": ["error", 0]
  }
}

const findJavaScriptFiles = (dir, excludedDirs = []) => {
  let filesToAnalyze = [];

  const walkDir = (currentPath) => {
    const files = fs.readdirSync(currentPath, { withFileTypes: true });
    for (const file of files) {
      const absolutePath = path.join(currentPath, file.name);
      if (file.isDirectory()) {
        // Skip excluded directories
        if (!excludedDirs.includes(file.name)) {
          walkDir(absolutePath);
        }
      } else if (/^(?!.*\.test\.(js|jsx|ts|tsx)$).*\.(js|jsx|ts|tsx|html)$/.test(file.name)) {
        filesToAnalyze.push({ absolutePath });
      }
    }
  };

  walkDir(dir);
  return filesToAnalyze;
};

function createReportItem() {
  return {
    reponame: "",
    filepath: "",
    filename: "",
    linesOfCode: 0,
    complexities: [],
    avrComplexity: 0,
    maxDepth: 0,
  };
}

(async function main() {
  const [directory, exclude] = process.argv.slice(2);
  const excludedDirs = exclude ? exclude.split(',').map(dir => dir.trim()) : [];

  if (!directory) {
    console.log("Usage: node script.js <directory> [<excludedDirs>]");
    process.exit(1);
  }

  const calculatedDepth = await madge(directory, MADGE_CONFIG).then((res) => calculateDepths(res.obj()))

  const files = findJavaScriptFiles(directory, excludedDirs);
  const repoName = path.basename(directory)

  if (files.length === 0) {
    console.log("No JavaScript files found.");
    return;
  }

  console.log(`Analyzing ${files.length} files...`);

  const eslint = new ESLint({
    useEslintrc: false,
    overrideConfig: ESLINT_CONFIG
  });
  const results = await eslint.lintFiles(files.map(file => file.absolutePath));

  let report = [];

  const complexityRegex = /complexity of (\d+)/;
  const locRegex = /File has too many lines \((\d+)\)/;

  results.forEach((result) => {
    let newReport = createReportItem();
    newReport.filepath = result.filePath;
    result.messages.forEach((message) => {
      if (message.ruleId === 'max-lines') {
        const match = message.message.match(locRegex);
        newReport.linesOfCode = match[1];
      }

      if (message.ruleId === 'complexity') {

        const match = message.message.match(complexityRegex);
        newReport.complexities.push(Number(match[1]));
      }
    });
    // add calculatedDepth to report
    const fileName = newReport.filepath.replace(path.join(directory, '/'), "");
    newReport.maxDepth = calculatedDepth[fileName] || 0
    newReport.filename = fileName
    newReport.reponame = repoName

    report.push(newReport);
  });

  report.forEach(item => {
    if (item.complexities.length !== 0) {
      item.complexities.forEach(complexity => {
        item.avrComplexity += Number(complexity)
      });
      // item.avrComplexity = Number(Math.ceil(item.avrComplexity / item.complexities.length));
    }
  });

  addToCsv(report)
  console.log(report);
})();


function addToCsv(data) {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
  const filePath = path.join(__dirname, 'data.csv');
  const exists = fs.existsSync(filePath);

  let csvContent = '';

  if (!exists) {
    csvContent += 'Repo,File,Complexity,LoC,Depth\n';
  }

  data.forEach(fileReport => {
    const dataToAdd = ["reponame", "filename", "avrComplexity", "linesOfCode", "maxDepth"].map(metric => fileReport[metric]).join(',')
    csvContent += dataToAdd + '\n'
  })

  csvContent += '\n'

  fs.appendFileSync(filePath, csvContent);
}