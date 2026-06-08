/// This file is based on `packages/server/src/models.py`

export type LiquidsoapMetadata = Partial<{
	artist: string;
	title: string;
	album: string;
	genre: string;
	date: string;
	tracknumber: string;
	comment: string;
	track: string;
	year: string;
	dj: string;
	next: string;
	metadata_url: string;
	coverart: string;
	cover: string;
	user: string;
	mode: string;
	playcount: string;
}>;
