<script lang="ts">
	import type { SvelteHTMLElements } from 'svelte/elements';

	const { width = 22, height = 11, ...rest }: SvelteHTMLElements['svg'] = $props();
</script>

<svg {width} {height} viewBox="0 0 22 11" fill="none" xmlns="http://www.w3.org/2000/svg" {...rest}>
	<path d="M0 11L11 0L22 11H0Z" fill="#34C759" />
</svg>
