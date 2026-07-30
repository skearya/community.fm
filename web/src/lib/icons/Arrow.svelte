<script lang="ts">
	import type { SvelteHTMLElements } from 'svelte/elements';

	const { width = 24, height = 24, ...rest }: SvelteHTMLElements['svg'] = $props();
</script>

<svg {width} {height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...rest}>
	<path d="M6.4 19L5 17.6L14.6 8H6V6H18V18H16V9.4L6.4 19Z" fill="currentColor" />
</svg>
