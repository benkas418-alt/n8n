// Runs the Apify TikTok Scraper once and writes CSV files to ./out.
// Usage: APIFY_TOKEN=... node run.mjs [--dry-run] [--from-file items.json]
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prepareVideos, topCreators } from './transform.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const input = JSON.parse(await readFile(join(here, 'input.json'), 'utf8'));

const nbSources = (input.hashtags?.length ?? 0) + (input.searchQueries?.length ?? 0) + (input.profiles?.length ?? 0);
const maxResults = nbSources * (input.resultsPerPage ?? 0);
console.log(`Sources: ${nbSources}, résultats max: ${maxResults}, coût max estimé: ~$${((maxResults / 1000) * 1.7).toFixed(2)} (tarif public $1.70/1000)`);
if (args.includes('--dry-run')) process.exit(0);

let items;
const fromFile = args[args.indexOf('--from-file') + 1];
if (args.includes('--from-file') && fromFile) {
	items = JSON.parse(await readFile(fromFile, 'utf8'));
} else {
	const token = process.env.APIFY_TOKEN;
	if (!token) {
		console.error('APIFY_TOKEN manquant. Créez-le sur https://console.apify.com/settings/integrations');
		process.exit(1);
	}
	const url = 'https://api.apify.com/v2/acts/clockworks~tiktok-scraper/run-sync-get-dataset-items?timeout=300';
	const res = await fetch(url, {
		method: 'POST',
		headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
		body: JSON.stringify(input),
	});
	if (!res.ok) {
		console.error(`Apify a répondu ${res.status}: ${(await res.text()).slice(0, 500)}`);
		process.exit(1);
	}
	items = await res.json();
}

const errors = items.filter((i) => i.errorCode);
const videos = prepareVideos(items, { maxAgeDays: 30 });
const creators = topCreators(videos);

const toCsv = (rows) => {
	if (!rows.length) return '';
	const cols = Object.keys(rows[0]);
	const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
	return [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n');
};

const outDir = join(here, 'out');
await mkdir(outDir, { recursive: true });
await writeFile(join(outDir, 'videos.csv'), toCsv(videos));
await writeFile(join(outDir, 'createurs.csv'), toCsv(creators));
console.log(`Bruts: ${items.length} | erreurs: ${errors.length} | vidéos retenues (<30 j): ${videos.length} | créateurs: ${creators.length}`);
for (const e of errors) console.log(`  ⚠ ${e.input ?? e.url}: ${e.errorCode}`);
console.log(`CSV écrits dans ${outDir}`);
