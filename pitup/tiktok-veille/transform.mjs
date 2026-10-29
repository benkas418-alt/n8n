// Pure functions shared by run.mjs and the n8n workflow (embedded by build-workflow.mjs).
// Keep them self-contained: no imports, no outer variables.

export function prepareVideos(items, { maxAgeDays = 30, now = Date.now() } = {}) {
	const seen = new Set();
	const videos = [];
	for (const v of items) {
		// The actor pushes "error items" (errorCode) for private/empty inputs.
		if (!v || v.errorCode || !v.id || seen.has(v.id)) continue;
		seen.add(v.id);
		const createdMs = v.createTimeISO ? Date.parse(v.createTimeISO) : NaN;
		if (Number.isFinite(createdMs) && now - createdMs > maxAgeDays * 86400000) continue;

		const a = v.authorMeta || {};
		const vues = v.playCount || 0;
		const likes = v.diggCount || 0;
		const commentaires = v.commentCount || 0;
		const partages = v.shareCount || 0;
		const enregistrements = v.collectCount || 0;
		const interactions = likes + commentaires + partages + enregistrements;
		videos.push({
			id: String(v.id),
			date: v.createTimeISO || '',
			source: v.searchQuery ? `recherche: ${v.searchQuery}` : v.input ? `entrée: ${v.input}` : 'hashtag',
			auteur: a.name ? `@${a.name}` : '',
			auteur_nom: a.nickName || '',
			auteur_url: a.profileUrl || '',
			abonnes: a.fans || 0,
			verifie: Boolean(a.verified),
			texte: (v.text || '').replace(/\s+/g, ' ').trim().slice(0, 300),
			hashtags: (v.hashtags || []).map((h) => h.name).filter(Boolean).join(' '),
			vues,
			likes,
			commentaires,
			partages,
			enregistrements,
			taux_engagement: vues ? Math.round((interactions / vues) * 10000) / 100 : 0,
			duree_s: (v.videoMeta && v.videoMeta.duration) || 0,
			sponsorise: Boolean(v.isAd || v.isSponsored),
			url: v.webVideoUrl || '',
			date_collecte: new Date(now).toISOString(),
		});
	}
	return videos.sort((x, y) => y.vues - x.vues);
}

export function topCreators(videos, { limit = 50 } = {}) {
	const byAuthor = new Map();
	for (const v of videos) {
		if (!v.auteur) continue;
		const c = byAuthor.get(v.auteur) || {
			auteur: v.auteur,
			auteur_nom: v.auteur_nom,
			auteur_url: v.auteur_url,
			abonnes: v.abonnes,
			verifie: v.verifie,
			nb_videos: 0,
			vues_totales: 0,
			somme_engagement: 0,
			meilleure_video: v.url,
			meilleures_vues: -1,
		};
		// Search results sometimes carry less author metadata than profile results.
		c.auteur_nom = c.auteur_nom || v.auteur_nom;
		c.auteur_url = c.auteur_url || v.auteur_url;
		c.abonnes = Math.max(c.abonnes, v.abonnes);
		c.nb_videos += 1;
		c.vues_totales += v.vues;
		c.somme_engagement += v.taux_engagement;
		if (v.vues > c.meilleures_vues) {
			c.meilleures_vues = v.vues;
			c.meilleure_video = v.url;
		}
		byAuthor.set(v.auteur, c);
	}
	return [...byAuthor.values()]
		.map(({ somme_engagement, meilleures_vues, ...c }) => ({
			...c,
			vues_moyennes: Math.round(c.vues_totales / c.nb_videos),
			engagement_moyen: Math.round((somme_engagement / c.nb_videos) * 100) / 100,
			date_collecte: videos[0] ? videos[0].date_collecte : new Date().toISOString(),
		}))
		.sort((x, y) => y.vues_moyennes - x.vues_moyennes)
		.slice(0, limit);
}
