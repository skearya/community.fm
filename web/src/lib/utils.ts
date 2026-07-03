import type { IcecastMetadata } from './types';

export function getListeners(status: IcecastMetadata) {
	try {
		// @ts-expect-error Icecast doesn't properly document.
		return status.icestats.source.reduce((acc, s) => acc + s.listeners, 0);
	} catch {
		return 0;
	}
}
