import type { Attachment } from 'svelte/attachments';

export function onClickOutside(handler: (event: PointerEvent) => void): Attachment {
	return (element) => {
		function handleClick(event: PointerEvent) {
			if (!element.contains(event.target as Node | null) && !event.defaultPrevented) {
				handler(event);
			}
		}

		document.addEventListener('click', handleClick, true);

		return () => {
			document.removeEventListener('click', handleClick, true);
		};
	};
}

export function memoize<Args extends unknown[], Return>(
	f: (...args: Args) => Return
): (...args: Args) => Return {
	const cache = new Map<string, Return>();

	return (...args: Args) => {
		const key = JSON.stringify(args);
		const cached = cache.get(key);

		if (cached !== undefined) return cached;

		const value = f(...args);
		cache.set(key, value);

		return value;
	};
}

export function wait(ms: number) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

export function unreachable(state: unknown) {
	throw new Error(`${state}`);
}
