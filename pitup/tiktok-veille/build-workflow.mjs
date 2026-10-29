// Generates workflow.json so the n8n Code nodes run the same logic as run.mjs.
// Usage: node build-workflow.mjs
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prepareVideos, topCreators } from './transform.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const input = JSON.parse(await readFile(join(here, 'input.json'), 'utf8'));

const sheet = (name, matchingColumn, position, id) => ({
	id,
	name: `Google Sheets – ${name}`,
	type: 'n8n-nodes-base.googleSheets',
	typeVersion: 4.5,
	position,
	parameters: {
		operation: 'appendOrUpdate',
		documentId: { __rl: true, mode: 'url', value: '' },
		sheetName: { __rl: true, mode: 'name', value: name },
		columns: { mappingMode: 'autoMapInputData', value: {}, matchingColumns: [matchingColumn] },
		options: {},
	},
});

const workflow = {
	name: 'PitUp – Veille TikTok Lubumbashi',
	nodes: [
		{
			id: 'a1b2c3d4-0001-4000-8000-000000000001',
			name: 'Chaque lundi 07:00',
			type: 'n8n-nodes-base.scheduleTrigger',
			typeVersion: 1.2,
			position: [0, 0],
			parameters: {
				rule: { interval: [{ field: 'weeks', triggerAtDay: [1], triggerAtHour: 7 }] },
			},
		},
		{
			id: 'a1b2c3d4-0002-4000-8000-000000000002',
			name: 'Apify – TikTok Scraper',
			type: 'n8n-nodes-base.httpRequest',
			typeVersion: 4.2,
			position: [220, 0],
			parameters: {
				method: 'POST',
				url: 'https://api.apify.com/v2/acts/clockworks~tiktok-scraper/run-sync-get-dataset-items',
				authentication: 'genericCredentialType',
				genericAuthType: 'httpHeaderAuth',
				sendQuery: true,
				queryParameters: { parameters: [{ name: 'timeout', value: '300' }] },
				sendBody: true,
				specifyBody: 'json',
				jsonBody: JSON.stringify(input, null, 2),
				options: { timeout: 330000 },
			},
			credentials: { httpHeaderAuth: { id: '', name: 'Apify API' } },
		},
		{
			id: 'a1b2c3d4-0003-4000-8000-000000000003',
			name: 'Préparer vidéos',
			type: 'n8n-nodes-base.code',
			typeVersion: 2,
			position: [440, 0],
			parameters: {
				jsCode: `${prepareVideos.toString()}\n\nreturn prepareVideos($input.all().map((i) => i.json), { maxAgeDays: 30 }).map((json) => ({ json }));\n`,
			},
		},
		{
			id: 'a1b2c3d4-0004-4000-8000-000000000004',
			name: 'Top créateurs',
			type: 'n8n-nodes-base.code',
			typeVersion: 2,
			position: [660, 160],
			parameters: {
				jsCode: `${topCreators.toString()}\n\nreturn topCreators($input.all().map((i) => i.json)).map((json) => ({ json }));\n`,
			},
		},
		sheet('videos', 'id', [660, -80], 'a1b2c3d4-0005-4000-8000-000000000005'),
		sheet('createurs', 'auteur', [880, 160], 'a1b2c3d4-0006-4000-8000-000000000006'),
	],
	connections: {
		'Chaque lundi 07:00': { main: [[{ node: 'Apify – TikTok Scraper', type: 'main', index: 0 }]] },
		'Apify – TikTok Scraper': { main: [[{ node: 'Préparer vidéos', type: 'main', index: 0 }]] },
		'Préparer vidéos': {
			main: [
				[
					{ node: 'Google Sheets – videos', type: 'main', index: 0 },
					{ node: 'Top créateurs', type: 'main', index: 0 },
				],
			],
		},
		'Top créateurs': { main: [[{ node: 'Google Sheets – createurs', type: 'main', index: 0 }]] },
	},
	settings: { executionOrder: 'v1', timezone: 'Africa/Lubumbashi' },
	pinData: {},
};

await writeFile(join(here, 'workflow.json'), `${JSON.stringify(workflow, null, '\t')}\n`);
console.log('workflow.json généré');
