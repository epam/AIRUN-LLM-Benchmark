function findMaxDepth(fileName, imports, visited = new Set()) {
  if (visited.has(fileName)) {
    return 0;
  }
  visited.add(fileName);

  if (!imports[fileName] || imports[fileName].length === 0) {
    return 0;
  }

  let maxDepth = 0;
  for (const imp of imports[fileName]) {
    const depth = findMaxDepth(imp, imports, new Set(visited)) + 1;
    maxDepth = Math.max(maxDepth, depth);
  }

  return maxDepth;
}

export default function calculateDepths(imports) {
  const result = {};
  for (const file in imports) {
    // result[file] = findMaxDepth(file, imports);
    result[file] = imports[file].length
  }
  return result;
}
