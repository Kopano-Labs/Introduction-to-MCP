#!/usr/bin/env node
/**
 * FivesArena Phase 0 evidence collector.
 *
 * Read-only: never modifies source files or assets.
 * Run from a checkout of Introduction-to-MCP and optionally point
 * FIVESARENA_REPO at a checkout of Bookit-5s-Arena.
 */
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { readFile, readdir, stat } from "node:fs/promises";
import { extname, join, relative, resolve } from "node:path";

const controlRoot = resolve(process.cwd());
const productRoot = resolve(process.env.FIVESARENA_REPO || "Bookit-5s-Arena");
const imageExtensions = new Set([".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".ico", ".glb", ".gltf"]);
const logoPattern = /(logo|brand|icon|mark|fives|5s.?arena)/i;
const worldCupPattern = /world\s*cup|wc2026|29.{0,5}31\s+may\s+2026|48\s*(teams|nations)/i;
const sensitiveRoutePattern = /\/(api\/)?(auth|account|admin|booking|payment|checkout|profile|user)/i;

async function walk(root, limit = 20000) {
  if (!existsSync(root)) return [];
  const files = [];
  const stack = [root];
  while (stack.length && files.length < limit) {
    const directory = stack.pop();
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      if ([".git", "node_modules", ".next", "dist", "build", ".venv", ".CLI_Project"].includes(entry.name)) continue;
      const path = join(directory, entry.name);
      if (entry.isDirectory()) stack.push(path);
      else if (entry.isFile()) files.push(path);
    }
  }
  return files;
}

async function sha256(path) {
  const bytes = await readFile(path);
  return createHash("sha256").update(bytes).digest("hex");
}

async function jsonFile(path) {
  if (!existsSync(path)) return null;
  return JSON.parse(await readFile(path, "utf8"));
}

async function textFile(path) {
  return existsSync(path) ? readFile(path, "utf8") : null;
}

async function inspectRoot(name, root) {
  const files = await walk(root);
  const assetCandidates = [];
  const staleClaims = [];

  for (const path of files) {
    const rel = relative(root, path).replaceAll("\\", "/");
    const extension = extname(path).toLowerCase();
    if (imageExtensions.has(extension) && logoPattern.test(rel)) {
      const info = await stat(path);
      assetCandidates.push({ path: rel, bytes: info.size, sha256: await sha256(path), extension });
    }
    if ([".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".html", ".md"].includes(extension)) {
      const content = await readFile(path, "utf8").catch(() => "");
      if (worldCupPattern.test(content)) staleClaims.push(rel);
    }
  }

  const packageJson = await jsonFile(join(root, "package.json"));
  const tsconfig = await jsonFile(join(root, "tsconfig.json"));
  const manifest = await jsonFile(join(root, "public", "manifest.json"));
  const serviceWorker = await textFile(join(root, "public", "sw.js"));

  const serviceWorkerRisks = [];
  if (serviceWorker) {
    if (/cache\.put\(event\.request/i.test(serviceWorker) && !/Cache-Control|authorization|credentials|sensitive/i.test(serviceWorker)) {
      serviceWorkerRisks.push("Broad runtime cache write without an explicit privacy exclusion signal.");
    }
    if (sensitiveRoutePattern.test(serviceWorker)) {
      serviceWorkerRisks.push("Sensitive-route strings appear in the service worker; review behavior manually.");
    }
  }

  return {
    name,
    root,
    exists: existsSync(root),
    assetCandidates: assetCandidates.sort((a, b) => a.path.localeCompare(b.path)),
    staleClaimFiles: staleClaims.sort(),
    toolchain: packageJson ? {
      typescript: packageJson.devDependencies?.typescript ?? packageJson.dependencies?.typescript ?? null,
      next: packageJson.dependencies?.next ?? packageJson.devDependencies?.next ?? null,
      eslintConfigNext: packageJson.devDependencies?.["eslint-config-next"] ?? null,
      three: packageJson.dependencies?.three ?? packageJson.devDependencies?.three ?? null,
      reactThreeFiber: packageJson.dependencies?.["@react-three/fiber"] ?? null,
    } : null,
    tsconfig: tsconfig ? {
      strict: tsconfig.compilerOptions?.strict ?? null,
      allowJs: tsconfig.compilerOptions?.allowJs ?? null,
      skipLibCheck: tsconfig.compilerOptions?.skipLibCheck ?? null,
      noUncheckedSideEffectImports: tsconfig.compilerOptions?.noUncheckedSideEffectImports ?? null,
      rootDir: tsconfig.compilerOptions?.rootDir ?? null,
      types: tsconfig.compilerOptions?.types ?? null,
    } : null,
    manifest: manifest ? {
      name: manifest.name ?? null,
      description: manifest.description ?? null,
      icons: manifest.icons ?? [],
    } : null,
    serviceWorkerRisks,
  };
}

const report = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  confidentiality: "No file contents, credentials, environment values, or private user data are emitted.",
  invariants: {
    logoMutationAllowed: false,
    auditMode: "read-only",
    controlPlane: "RobynAwesome/Introduction-to-MCP",
  },
  roots: [
    await inspectRoot("control-plane", controlRoot),
    await inspectRoot("production-candidate", productRoot),
  ],
};

process.stdout.write(JSON.stringify(report, null, 2) + "\n");
