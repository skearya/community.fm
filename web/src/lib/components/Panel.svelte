<script lang="ts">
	import type { IcecastMetadata } from '$lib/types';
	import { fade, fly } from 'svelte/transition';
	import { onClickOutside } from '$lib/utils';
	import Plus from '$lib/icons/Plus.svelte';
	import { cubicOut } from 'svelte/easing';
	import Icecast from '$lib/icons/Icecast.svelte';
	import GitHub from '$lib/icons/GitHub.svelte';

	type Props = {
		stream: string;
		icecast: IcecastMetadata;
		src: string | null;
	};

	let { stream, icecast, src }: Props = $props();

	let showPanel = $state(false);

	let stats = $derived.by<[string, string][] | null>(() => {
		if (!icecast) return null;
		if (!src) return null;

		const pathname = new URL(src).pathname;

		try {
			// @ts-expect-error Icecast doesn't properly document.
			const source = icecast.icestats.source.find((source) => source.listenurl.endsWith(pathname))!;

			return source.audio_info.split(';').map((data: string) => data.split('='));
		} catch {
			return null;
		}
	});
</script>

<button
	class="fixed right-7.5 bottom-8 z-20 flex items-center gap-x-1.5 rounded-[3.6875rem] bg-foreground px-5 py-3.75 text-background xl:right-auto xl:left-7.5"
	onclick={!showPanel ? () => (showPanel = true) : undefined}
>
	<Plus class={['transition-transform duration-500 ease-spring', showPanel && 'rotate-45']} />
	<p class="hidden text-[1.375rem] leading-6.5 tracking-wide lg:block">community.fm</p>

	{#if showPanel}
		<div
			transition:fly={{ duration: 150, y: 8 }}
			class="absolute -top-3 right-0 -translate-y-full space-y-3 rounded-2xl bg-foreground p-3.75 text-left text-nowrap text-background shadow select-text xl:right-auto xl:left-0"
			{@attach onClickOutside((e) => {
				e.stopPropagation();
				showPanel = false;
			})}
		>
			{#if stats && stats.length > 0}
				<div>
					{#each stats as [name, value] (name)}
						<p class="font-mono text-lg">{name} = {value}</p>
					{/each}
				</div>
			{/if}
			<div class="flex justify-center space-x-3">
				<a href={stream} rel="external" target="_blank">
					<Icecast width={48} height={48} />
				</a>
				<a href="https://github.com/skearya/community.fm" rel="external" target="_blank">
					<GitHub width={48} height={48} />
				</a>
			</div>
		</div>
	{/if}
</button>

{#if showPanel}
	<div
		transition:fade={{ easing: cubicOut, duration: 150 }}
		class="background fixed top-0 left-0 z-10 h-full w-full"
	></div>
{/if}

<style>
	.background {
		background-image: radial-gradient(at bottom right, var(--color-background), transparent);
	}

	@media (min-width: 80rem) {
		.background {
			background-image: radial-gradient(at bottom left, var(--color-background), transparent);
		}
	}
</style>
