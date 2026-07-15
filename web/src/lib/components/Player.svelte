<script lang="ts">
	import type { Data, LiquidsoapMetadata } from '$lib/types';
	import { onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import Circle from '$lib/icons/Circle.svelte';
	import Person from '$lib/icons/Person.svelte';
	import Play from '$lib/icons/Play.svelte';
	import Volume from '$lib/icons/Volume.svelte';
	import Avatar from '$lib/components/Avatar.svelte';
	import { flip, cloneOver } from '$lib/animation';
	import { getListeners } from '$lib/utils';

	let { stream, history, liquidsoap: metadata, icecast }: Data = $props();

	let leftElement: HTMLElement;
	let rightElement: HTMLElement;
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

	const easeOut = 'cubic-bezier(0.23, 1, 0.32, 1)';

	let leftElementPos: DOMRect | null = null;
	let rightElementPos: DOMRect | null = null;

	$effect.pre(() => {
		void show;

		if (leftElement) leftElementPos = leftElement.getBoundingClientRect();
		if (rightElement) rightElementPos = rightElement.getBoundingClientRect();
	});

	$effect(() => {
		void show;

		if (!leftElementPos || !rightElementPos) return;

		const animations: Animation[] = [];

		animations.push(
			flip(
				leftElement,
				{ from: leftElementPos, to: leftElement.getBoundingClientRect() },
				{ duration: 500, easing: easeOut }
			)
		);

		if (show) {
			animations.push(
				rightElement.animate(
					{ opacity: ['0%', '100%'], scale: ['90%', '100%'] },
					{ duration: 500, easing: easeOut }
				)
			);
		} else {
			const rightElementClone = cloneOver(rightElement, rightElementPos);
			rightElementClone.style.display = 'block';

			const rightElementAnimation = rightElementClone.animate(
				{ opacity: ['100%', '0%'], scale: '90%' },
				{ duration: 500, easing: easeOut }
			);

			rightElementAnimation.addEventListener('finish', () => rightElementClone.remove());
			rightElementAnimation.addEventListener('cancel', () => rightElementClone.remove());

			animations.push(rightElementAnimation);
		}

		return () => animations.forEach((a) => a.cancel());
	});

	let title = $derived(`${metadata?.title} - ${metadata?.artist}`);
	let trackHistory = $derived(history.toReversed().slice(1));

	onDestroy(() => disconnect());
</script>

<svelte:head>
	<title>{title}</title>
	{#if metadata?.cover}<link rel="icon" href={metadata.cover} />{/if}
</svelte:head>

<main in:fade={{ duration: 125 }} class="mx-auto max-w-360">
	<nav class="flex items-center justify-between px-7.5 pt-8">
		{#if metadata?.user}
			<div class="flex gap-x-3.75">
				<Avatar username={metadata.user} url={metadata?.avatar} class="size-12.75" />
				<div>
					<p class="text-[22px] leading-6.5 tracking-wide text-gray">DJ</p>
					<p class="text-[22px] leading-6.5 tracking-wide">{metadata?.user}</p>
				</div>
			</div>
		{/if}
		<div class="ml-20 flex flex-1 justify-start gap-x-12.5">
			{#each [['Play Count', metadata?.playcount]] as [name, value] (name)}
				{#if value}
					<div>
						<p class="text-[22px] leading-6.5 tracking-wide text-gray">{name}</p>
						<p class="text-[22px] leading-6.5 tracking-wide">{value}</p>
					</div>
				{/if}
			{/each}
		</div>
		<div class="flex items-center gap-x-3 text-nowrap">
			<div class="flex gap-x-1.5 rounded-[59px] bg-foreground px-5 py-3.75 text-background">
				<Person />
				<p class="text-[22px] leading-6.5 tracking-wide">{getListeners(icecast)} Listeners</p>
			</div>
			<div class="flex gap-x-1.5 rounded-[59px] bg-red px-5 py-3.75 text-background">
				<Circle />
				<p class="text-[22px] leading-6.5 tracking-wide">{metadata?.mode}</p>
			</div>
			<button
				class="group relative flex gap-x-1.5 rounded-[59px] bg-light-gray px-5 py-3.75 text-background"
			>
				<Volume />
				<div class="absolute bottom-0 left-0 h-full w-full translate-y-1/2 opacity-0"></div>
				<div
					class="absolute -bottom-2 left-1/2 z-20 hidden -translate-x-1/2 translate-y-full rounded-[59px] bg-light-gray px-3.75 py-5 shadow group-hover:block"
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
		style="height: clamp(30px, calc(30px + (100vh - 850px) * (60 - 30) / (1080 - 850)), 60px);"
	></div>

	<div
		class={[
			'mx-auto flex max-w-288.5 items-start px-7.5',
			show ? 'justify-between' : 'justify-center'
		]}
	>
		<div
			bind:this={leftElement}
			class="group z-10 flex w-125.75 flex-col items-stretch will-change-transform"
			{title}
		>
			<p class="mb-1.5 truncate text-[48px] leading-14.25 font-medium">
				{metadata?.title ?? 'Unknown Title'}
			</p>
			<p class="mb-7.5 truncate text-[32px] leading-9.5 text-gray">
				{metadata?.artist ?? 'Unknown Artist'}
			</p>
			<button
				class="relative overflow-hidden rounded-[83px] transition-transform active:scale-95"
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

		<section
			bind:this={rightElement}
			class={['mt-3.5 w-108.75 will-change-transform', show ? 'block' : 'hidden']}
		>
			<p class="mb-6 leading-4.75 tracking-[-0.02em] text-gray">Previous songs</p>
			<div
				bind:this={historyElement}
				style="scrollbar-width: none;"
				class="max-h-144.5 snap-y space-y-4.25 overflow-y-auto rounded-2xl"
			>
				{#each trackHistory as [track, time] (time)}
					{@render previous(track)}
				{:else}
					<p>...</p>
				{/each}
			</div>
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
			<div class="mb-3.5 text-[22px] leading-7.5">
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
