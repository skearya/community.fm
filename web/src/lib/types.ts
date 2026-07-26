/// Based on `packages/server/src/models.py` and `packages/server/src/server.py`

export type Data = {
	stream: string;
	modes: string[];
	icecast: IcecastMetadata;
	liquidsoap: LiquidsoapEntry;
	history: LiquidsoapEntry[];
};

export type Message =
	| ({ type: 'info' } & Data)
	| { type: 'icecast'; data: IcecastMetadata }
	| { type: 'liquidsoap'; data: LiquidsoapEntry };

export type IcecastMetadata = unknown;

export type LiquidsoapEntry = {
	id: string;
	time: number;
	metadata: LiquidsoapMetadata;
	has_cover: boolean;
};

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
	user: string;
	avatar: string;
	mode: string;
	playcount: string;
}>;
