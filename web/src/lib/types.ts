/// This file is based on `packages/server/src/models.py`

type IcecastSource = Partial<{
	audio_info: string;
	bitrate: number;
	channels: number;
	genre: string;
	listener_peak: number;
	listeners: number;
	listenurl: string;
	samplerate: number;
	server_description: string;
	server_name: string;
	server_type: string;
	stringeam_start: string;
	stringeam_start_iso8601: string;
	title: string;
	dummy: boolean;
	artist: string;
	audio_bitrate: number;
	audio_channels: number;
	audio_samplerate: number;
	ice_bitrate: number;
	subtype: string;
}>;

export type IcecastStatus = Partial<{
	admin: string;
	host: string;
	location: string;
	server_id: string;
	server_start: string;
	server_start_iso8601: string;
	source: IcecastSource[];
}>;

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
}>;
