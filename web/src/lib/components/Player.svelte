<script lang="ts">
	import type { Data } from '$lib/types';
	import { fade } from 'svelte/transition';
	import Arrow from '$lib/icons/Arrow.svelte';
	import Circle from '$lib/icons/Circle.svelte';
	import Person from '$lib/icons/Person.svelte';
	import Play from '$lib/icons/Play.svelte';
	import Volume from '$lib/icons/Volume.svelte';
	import { flip, cloneOver } from '$lib/animation';
	import { getListeners } from '$lib/utils';

	let { stream, metadata, status, modes }: Data = $props();

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

		audio.load();
		await audio.play();

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

	const easeOut = 'cubic-bezier(0.23, 1, 0.32, 1)';

	let leftElement: HTMLElement;
	let leftElementPos: DOMRect | null = null;
	let leftAnimation: Animation | null = null;

	let rightElement: HTMLElement;
	let rightElementPos: DOMRect | null = null;
	let rightAnimation: Animation | null = null;

	$effect.pre(() => {
		void show;

		if (leftElement) {
			leftElementPos = leftElement.getBoundingClientRect();
			leftAnimation?.cancel();
		}

		if (rightElement) {
			rightElementPos = rightElement.getBoundingClientRect();
			rightAnimation?.cancel();
		}
	});

	$effect(() => {
		void show;

		if (!leftElementPos || !rightElementPos) return;

		const leftElementCurrentPos = leftElement.getBoundingClientRect();

		leftAnimation = flip(
			leftElement,
			{ from: leftElementPos, to: leftElementCurrentPos },
			{ duration: 500, easing: easeOut }
		);

		if (show) {
			rightAnimation = rightElement.animate(
				{ opacity: ['0%', '100%'], scale: ['90%', '100%'] },
				{ duration: 500, easing: easeOut }
			);
		} else {
			const rightElementClone = cloneOver(rightElement, rightElementPos);
			rightElementClone.style.display = 'block';

			rightElementClone
				.animate({ opacity: ['100%', '0%'], scale: '90%' }, { duration: 500, easing: easeOut })
				.addEventListener('finish', () => rightElementClone.remove());
		}
	});

	let title = $derived(`${metadata?.title} - ${metadata?.artist}`);
</script>

<svelte:head>
	<title>{title}</title>
	{#if metadata?.cover}<link rel="icon" href={metadata.cover} />{/if}
</svelte:head>

<main in:fade={{ duration: 125 }} class="mx-auto max-w-360">
	<nav class="flex items-center justify-between px-7.5 pt-8">
		<div class="flex gap-x-3.75">
			<img
				src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
				alt="avatar"
				class="size-12.75 rounded-full"
			/>
			<div>
				<p class="text-[22px] leading-6.5 tracking-wide text-gray">DJ</p>
				<div class="flex items-center">
					<p class="text-[22px] leading-6.5 tracking-wide">skeary</p>
					<Arrow />
				</div>
			</div>
			<div class="ml-25 flex gap-x-12.5">
				<div>
					<p class="text-[22px] leading-6.5 tracking-wide text-gray">Times played</p>
					<p class="text-[22px] leading-6.5 tracking-wide">10,8378</p>
				</div>
				<div>
					<p class="text-[22px] leading-6.5 tracking-wide text-gray">Times played</p>
					<p class="text-[22px] leading-6.5 tracking-wide">10,8378</p>
				</div>
			</div>
		</div>
		<div class="flex items-center gap-x-3 text-nowrap">
			<div class="flex gap-x-1.5 rounded-[59px] bg-foreground px-5 py-3.75 text-background">
				<Person />
				<p class="text-[22px] leading-6.5 tracking-wide">{getListeners(status)} Listeners</p>
			</div>
			<div class="flex gap-x-1.5 rounded-[59px] bg-red px-5 py-3.75 text-background">
				<Circle />
				<p class="text-[22px] leading-6.5 tracking-wide">Live</p>
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
				{#if metadata?.cover}
					<img
						src={metadata.cover}
						alt="cover"
						draggable="false"
						class={[
							'w-full min-w-0 object-cover transition-[filter]',
							(!show || loading) && 'brightness-50'
						]}
					/>
				{:else}
					<div
						class={[
							'aspect-square w-full bg-gray transition-[filter]',
							(!show || loading) && 'brightness-50'
						]}
					></div>
				{/if}
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
				style="scrollbar-width: none;"
				class="max-h-144.5 snap-y space-y-4.25 overflow-y-auto rounded-2xl"
			>
				{#each { length: 50 }}
					{@render previous()}
				{/each}
			</div>
		</section>
	</div>
</main>

{#snippet previous()}
	<div class="flex snap-start gap-x-5.5">
		<img
			src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
			alt="cover"
			class="size-25.5 rounded-2xl"
		/>
		<div class="min-w-0 flex-1">
			<div class="mb-3.5 text-[22px] leading-7.5">
				<p class="truncate">Nothing Even Matters (D’Angelo)</p>
				<p class="truncate text-gray">Ms. Lauryn Hill</p>
			</div>
			<div class="flex gap-x-3.25">
				<div class="flex items-center gap-x-1.25 text-gray">
					<Person />
					<p>skeary</p>
				</div>
			</div>
		</div>
	</div>
{/snippet}
