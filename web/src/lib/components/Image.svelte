<!-- https://github.com/vercel/avatar/blob/master/utils/gradient.ts -->

<script lang="ts" module>
	import color from 'tinycolor2';
	import { memoize } from '$lib/utils';

	function hash(str: string) {
		let hash = 0;

		for (let i = 0, len = str.length; i < len; i++) {
			let chr = str.charCodeAt(i);
			hash = (hash << 5) - hash + chr;
			hash |= 0;
		}

		return hash;
	}

	export const generateGradient = memoize((username: string) => {
		const first = color({ h: hash(username) % 360, s: 0.95, l: 0.5 });
		const second = first.triad()[1];

		return {
			fromColor: first.toHexString(),
			toColor: second.toHexString()
		};
	});
</script>

<script lang="ts">
	import type { ClassValue, SvelteHTMLElements } from 'svelte/elements';

	let {
		url,
		key,
		class: className,
		...rest
	}: {
		url: string | undefined;
		key: string;
	} & SvelteHTMLElements['img'] &
		SvelteHTMLElements['div'] = $props();

	let status = $state<'loading' | 'loaded' | 'error'>('loading');

	const containerClass = $derived<ClassValue>([
		rest.loading === 'lazy' && 'opacity-0 transition-opacity',
		rest.loading === 'lazy' && status !== 'loading' && 'opacity-100',
		status !== 'loaded' && 'aspect-square',
		className
	]);

	const gradientStyle = $derived.by(() => {
		const { fromColor, toColor } = generateGradient(key);

		return `background: linear-gradient(135deg, ${fromColor} 0%, ${toColor} 100%);`;
	});

	$effect(() => {
		void url;

		status = 'loading';
	});
</script>

{#if url !== undefined && status !== 'error'}
	<img
		src={url}
		alt=""
		class={containerClass}
		onload={() => (status = 'loaded')}
		onerror={() => (status = 'error')}
		{...rest}
	/>
{:else}
	<div style={gradientStyle} class={containerClass} {...rest}></div>
{/if}
