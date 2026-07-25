<script lang="ts">
	import type { Data, LiquidsoapMetadata } from '$lib/types';
	import { onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import Circle from '$lib/icons/Circle.svelte';
	import Person from '$lib/icons/Person.svelte';
	import Play from '$lib/icons/Play.svelte';
	import Volume from '$lib/icons/Volume.svelte';
	import Avatar from '$lib/components/Avatar.svelte';
	import { getListeners } from '$lib/utils';

	let { stream, history, liquidsoap: metadata, icecast }: Data = $props();

	let historyElement: HTMLElement;

	let show = $state(false);
	let loading = $state(false);
	let volumeLevel = $state(50);

	let audio: HTMLAudioElement | null = null;

	async function connect() {
		audio = new Audio();
		audio.preload = 'none';
		audio.volume = volumeLevel / 100;
		audio.src =
			new URL('stream.ogg', stream) + '?' + new URLSearchParams({ cache: `${Date.now()}` });

		loading = true;

		try {
			audio.load();
			await audio.play();
		} catch {
			audio.src =
				new URL('stream.mp3', stream) + '?' + new URLSearchParams({ cache: `${Date.now()}` });

			audio.load();
			await audio.play();
		}

		loading = false;
	}

	function disconnect() {
		if (!audio) return;

		audio.pause();
		audio.src = '';
		audio.removeAttribute('src');
		audio = null;
	}

	$effect(() => {
		void volumeLevel;

		if (audio !== null) {
			audio.volume = volumeLevel / 100;
		}
	});

	$effect(() => {
		void trackHistory.length;

		if (historyElement) {
			historyElement.scrollTo({ top: 0, behavior: 'smooth' });
		}
	});

	let title = $derived(`${metadata?.title} - ${metadata?.artist}`);
	let trackHistory = $derived(history.toReversed().slice(1));

	onDestroy(() => disconnect());
</script>

<svelte:head>
	<title>{title}</title>
	{#if metadata?.cover}<link rel="icon" href={metadata.cover} />{/if}
</svelte:head>

<main in:fade={{ duration: 125 }} class="mx-auto flex max-w-360 flex-col gap-8.75 xl:h-screen">
	<nav class="flex items-center justify-between gap-y-3.75 px-7.5 pt-8 text-nowrap xl:flex-row">
		{#if metadata?.user}
			<div class="flex gap-x-3.75">
				<Avatar username={metadata.user} url={metadata?.avatar} class="size-12.75" />
				<div>
					<p class="text-[1.375rem] leading-6.5 tracking-wide text-gray">DJ</p>
					<p class="text-[1.375rem] leading-6.5 tracking-wide">{metadata?.user}</p>
				</div>
			</div>
		{/if}
		<div class="ml-20 hidden flex-1 justify-start gap-x-12.5 xl:flex">
			{#each [['Play Count', metadata?.playcount]] as [name, value] (name)}
				{#if value}
					<div>
						<p class="text-[1.375rem] leading-6.5 tracking-wide text-gray">{name}</p>
						<p class="text-[1.375rem] leading-6.5 tracking-wide">{value}</p>
					</div>
				{/if}
			{/each}
		</div>
		<div class="flex items-center gap-x-3">
			<div
				class="flex items-center gap-x-1.5 rounded-[3.6875rem] bg-foreground px-5 py-3.75 text-background"
			>
				<Person />
				<p class="text-[1.375rem] leading-6.5 tracking-wide">
					{getListeners(icecast)} <span class="hidden xl:inline">Listeners</span>
				</p>
			</div>
			<div
				class="flex items-center gap-x-1.5 rounded-[3.6875rem] bg-red px-5 py-3.75 text-background"
			>
				<Circle />
				<p class="hidden text-[1.375rem] leading-6.5 tracking-wide xl:block">{metadata?.mode}</p>
			</div>
			<button
				class="group relative hidden gap-x-1.5 rounded-[3.6875rem] bg-light-gray px-5 py-3.75 text-background xl:flex"
			>
				<Volume />
				<div class="absolute bottom-0 left-0 h-full w-full translate-y-1/2 opacity-0"></div>
				<div
					class="absolute -bottom-2 left-1/2 z-20 hidden -translate-x-1/2 translate-y-full rounded-[3.6875rem] bg-light-gray px-3.75 py-5 shadow group-hover:block"
				>
					<input
						bind:value={volumeLevel}
						type="range"
						min="0"
						max="100"
						style="writing-mode: vertical-lr; direction: rtl;"
						class="accent-dark-gray"
					/>
				</div>
			</button>
		</div>
	</nav>

	<div
		class="mx-auto flex h-full w-full max-w-288.5 flex-col items-center justify-between gap-y-8.75 overflow-hidden px-7.5 xl:flex-row xl:items-start"
	>
		<div class="group z-10 flex w-full max-w-125.75 min-w-0 flex-col items-stretch" {title}>
			<p class="mb-1.5 truncate text-[3rem] leading-14.25 font-medium">
				{metadata?.title ?? 'Unknown Title'}
			</p>
			<p class="mb-7.5 truncate text-[2rem] leading-9.5 text-gray">
				{metadata?.artist ?? 'Unknown Artist'}
			</p>
			<button
				class="relative overflow-hidden rounded-[5rem] transition-transform duration-1000 ease-spring active:scale-95"
				onclick={() => {
					show = !show;

					if (show) {
						connect();
					} else {
						disconnect();
					}
				}}
			>
				<Avatar
					url={metadata?.cover}
					username={metadata?.title ?? '?'}
					rounded={false}
					draggable={false}
					class={[
						'w-full min-w-0 object-cover transition-[filter]',
						(!show || loading) && 'brightness-50',
						!metadata?.cover && 'aspect-square'
					]}
				/>
				<div
					class={[
						'absolute top-1/2 left-1/2 -translate-1/2 mix-blend-exclusion transition-opacity duration-100',
						show ? 'opacity-0' : 'opacity-100'
					]}
				>
					<Play />
				</div>
			</button>
		</div>

		<section class="relative flex h-full w-full flex-col xl:w-108.75">
			<p class="mt-3.5 mb-6 leading-4.75 tracking-[-0.02em] text-gray">Previous songs</p>
			<div
				bind:this={historyElement}
				style="scrollbar-width: none;"
				class="snap-y space-y-4.25 overflow-y-auto rounded-t-2xl pb-6"
			>
				{#each trackHistory as [track, time] (time)}
					{@render previous(track)}
				{:else}
					<p>...</p>
				{/each}
			</div>
			<div
				class="pointer-events-none absolute bottom-0 left-0 hidden h-16 w-full bg-linear-to-t from-background to-transparent xl:block"
			></div>
		</section>
	</div>
</main>

{#snippet previous(metadata: LiquidsoapMetadata)}
	<div class="flex snap-start gap-x-5.5">
		<Avatar
			url={metadata?.cover}
			username={metadata?.title ?? 'Unknown'}
			rounded={false}
			class="aspect-square size-25.5 rounded-2xl object-cover"
		/>
		<div class="min-w-0 flex-1">
			<div class="mb-3.5 text-[1.375rem] leading-7.5">
				<p class="truncate">{metadata.title}</p>
				<p class="truncate text-gray">{metadata.artist}</p>
			</div>
			<div class="flex gap-x-3.25">
				{#if metadata?.user}
					<div class="flex items-center gap-x-2.25 text-gray">
						<Avatar url={metadata?.avatar} username={metadata.user} class="size-6" />
						<p>{metadata.user}</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/snippet}
