<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta property="og:title" content="community.fm" />
	<meta property="og:type" content="music.radio_station" />
</svelte:head>

{@render children()}
