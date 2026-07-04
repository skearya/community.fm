import type { IcecastMetadata } from '$lib/types';

export function getListeners(status: IcecastMetadata) {
	try {
		// @ts-expect-error Icecast doesn't properly document.
		return status.icestats.source.reduce((acc, s) => acc + s.listeners, 0);
	} catch {
		return 0;
	}
}

export function wait(ms: number) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

export function unreachable(state: unknown) {
	throw new Error(`${state}`);
}
