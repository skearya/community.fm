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
	import type { SvelteHTMLElements } from 'svelte/elements';

	let {
		url,
		username,
		rounded = true,
		class: className,
		...rest
	}: {
		url?: string;
		username: string;
		rounded?: boolean;
	} & SvelteHTMLElements['img'] &
		SvelteHTMLElements['div'] = $props();

	const containerClass = () => [rounded && 'rounded-full', className];
</script>

{#if url}
	<img src={url} alt={username} class={containerClass()} {...rest} />
{:else}
	{@const { fromColor, toColor } = generateGradient(username)}

	<div
		class={containerClass()}
		style={`background: linear-gradient(135deg, ${fromColor} 0%, ${toColor} 100%);`}
		{...rest}
	></div>
{/if}
