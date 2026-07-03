export type Data = {
	stream: string;
	metadata: LiquidsoapMetadata | null;
	status: IcecastMetadata | null;
	modes: string[];
};

/// Based on `packages/server/src/server.py`
export type Message =
	| ({ type: 'info' } & Data)
	| { type: 'metadata'; metadata: LiquidsoapMetadata }
	| { type: 'status'; status: unknown };

/// Based on `packages/server/src/models.py`
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

export type IcecastMetadata = unknown;
