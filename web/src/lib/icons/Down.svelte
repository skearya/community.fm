<script lang="ts">
	import type { SvelteHTMLElements } from 'svelte/elements';

	const { width = 22, height = 11, ...rest }: SvelteHTMLElements['svg'] = $props();
</script>

<svg {width} {height} viewBox="0 0 22 11" fill="none" xmlns="http://www.w3.org/2000/svg" {...rest}>
	<path d="M22 0L11 11L9.61651e-07 -1.9233e-06L22 0Z" fill="#AEAEB2" />
</svg>
