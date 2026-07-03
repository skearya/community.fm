<script lang="ts">
	import type { Data } from '$lib/types';
	import { fade } from 'svelte/transition';
	import Arrow from '$lib/icons/Arrow.svelte';
	import Circle from '$lib/icons/Circle.svelte';
	import Down from '$lib/icons/Down.svelte';
	import Person from '$lib/icons/Person.svelte';
	import Play from '$lib/icons/Play.svelte';
	import Up from '$lib/icons/Up.svelte';
	import Volume from '$lib/icons/Volume.svelte';
	import { flip, cloneOver } from '$lib/animation';
	import { getListeners } from '$lib/utils';

	let { stream, metadata, status, modes }: Data = $props();

	let show = $state(false);
	let volumeLevel = $state(50);

	let audio: HTMLAudioElement | null = null;

	function connect() {
		audio = new Audio();
		audio.preload = 'none';
		audio.volume = volumeLevel / 100;
		audio.src =
			new URL('stream.ogg', stream) + '?' + new URLSearchParams({ cache: `${Date.now()}` });

		audio.load();
		audio.play();
	}

	function disconnect() {
		if (audio) {
			audio.pause();
			audio.src = '';
			audio.removeAttribute('src');
			audio = null;
		}
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

		if (leftElement) {
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

<main
	in:fade={{ duration: 125 }}
	style="gap: clamp(30px, calc(30px + (100vh - 850px) * 30 / (1080 - 850)), 60px);"
	class="mx-auto flex max-w-360 flex-col"
>
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
					<p class="text-[22px] leading-6.5 tracking-wide">Skeary</p>
					<Arrow />
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
		class={[
			'mx-auto flex w-full max-w-288.5 flex-col items-center justify-start gap-y-26.25 px-7.5 pb-8 xl:flex-row xl:items-stretch',
			show ? 'xl:justify-between' : 'xl:justify-center'
		]}
	>
		<div
			bind:this={leftElement}
			class="group z-10 flex flex-col text-left will-change-transform"
			{title}
		>
			<p class="mb-1.5 truncate text-[48px] leading-14.25 font-medium">{metadata?.title}</p>
			<p class="mb-7.5 truncate text-[32px] leading-9.5 text-gray">{metadata?.artist}</p>
			<button
				class="relative transition-transform active:scale-95"
				onclick={() => {
					show = !show;

					if (show) {
						connect();
					} else {
						disconnect();
					}
				}}
			>
				<div
					class={[
						'absolute top-1/2 left-1/2 z-10 -translate-1/2 mix-blend-difference transition-opacity duration-50',
						show ? 'opacity-0' : 'opacity-100'
					]}
				>
					<Play />
				</div>
				<img
					draggable="false"
					src={metadata?.cover}
					alt="cover"
					class={[
						'aspect-square max-h-125.75 min-h-0 rounded-[83px] object-contain transition-[filter]',
						!show && 'brightness-50'
					]}
				/>
			</button>
		</div>

		<section
			bind:this={rightElement}
			class={['self-stretch will-change-transform xl:max-w-108.75', show ? 'block' : 'hidden']}
		>
			<p class="mb-6 leading-4.75 tracking-[-0.02em] text-gray">Previous songs</p>
			<div class="flex flex-col gap-y-4.25">
				{#each { length: 5 }}
					{@render previous()}
				{/each}
			</div>
		</section>
	</div>
</main>

{#snippet previous()}
	<div class="flex gap-x-5.5">
		<img
			src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
			alt="cover"
			class="size-25.5 rounded-2xl"
		/>
		<div class="min-w-0 flex-1">
			<div class="mb-3 text-[22px] leading-7.5">
				<p class="truncate">
					Lorem ipsum dolor sit amet consectetur adipisicing elit. Iste placeat laboriosam
					aspernatur vel esse modi corporis minima, nostrum quas sapiente incidunt recusandae
					cupiditate sequi, consequatur tempora accusantium aliquam nemo molestias. Nothing Even
					Matters (D’Angelo)
				</p>
				<p class="truncate text-gray">Ms. Lauryn Hill</p>
			</div>
			<div class="flex gap-x-3.25">
				<div class="flex items-center gap-1.25">
					<Up />
					<p class="text-[22px] leading-6.5">11</p>
				</div>
				<div class="flex items-center gap-1.25">
					<Down />
					<p class="text-[22px] leading-6.5">2</p>
				</div>
			</div>
		</div>
	</div>
{/snippet}
