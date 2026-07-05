export type Data = {
	stream: string;
	modes: string[];
	history: [LiquidsoapMetadata, number][];
	liquidsoap: LiquidsoapMetadata;
	icecast: IcecastMetadata;
};

/// Based on `packages/server/src/server.py`
export type Message =
	| ({ type: 'info' } & Data)
	| { type: 'liquidsoap'; liquidsoap: LiquidsoapMetadata }
	| { type: 'icecast'; icecast: IcecastMetadata };

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
	avatar: string;
	mode: string;
	playcount: string;
}>;

export type IcecastMetadata = unknown;
