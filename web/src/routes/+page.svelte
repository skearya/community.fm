<script lang="ts">
	import { onMount } from 'svelte';

	type Data = {
		stream: string;
		metadata: Record<string, string | null> | null;
		modes: string[];
	};

	type State =
		| { type: 'awaiting' }
		| { type: 'connected' }
		| { type: 'ready'; data: Data }
		| { type: 'error'; reason: string };

	type Message = ({ type: 'info' } & Data) | { type: 'metadata'; metadata: Data['metadata'] };

	let s = $state<State>({ type: 'awaiting' });

	onMount(() => {
		const eventSource = new EventSource('/api/subscribe');

		eventSource.addEventListener('open', () => {
			s = { type: 'connected' };
		});

		eventSource.addEventListener('message', (event) => {
			const message = JSON.parse(event.data) as Message;

			switch (message.type) {
				case 'info':
					s = { type: 'ready', data: message };
					break;
				case 'metadata':
					if (s.type !== 'ready') throw new Error();

					s.data.metadata = message.metadata;
					break;
				default:
					message satisfies never;
			}
		});

		eventSource.addEventListener('error', (event) => {
			console.error('Connection failed', event);
			s = { type: 'error', reason: `${eventSource.readyState}` };
		});
	});

	let showInfo = $state(true);

	let title = $derived(
		s.type === 'ready' ? `${s.data.metadata?.title} - ${s.data.metadata?.artist}` : s.type
	);
</script>

<svelte:head>
	<title>{title}</title>
	{#if s.type === 'ready' && s.data.metadata?.cover}
		<link rel="icon" href={s.data.metadata.cover} />
	{/if}
</svelte:head>

<main class="flex h-dvh items-center justify-center">
	{#if s.type === 'awaiting'}
		<pre>connecting</pre>
	{:else if s.type === 'connected'}
		<pre>connected</pre>
	{:else if s.type === 'ready'}
		<section
			{title}
			class="relative z-1 flex max-w-64 flex-col items-stretch border border-white/25 md:max-w-80"
		>
			<div
				class="absolute top-2.5 left-0 flex -translate-x-[calc(100%+1px)] flex-col items-end gap-1.5"
			>
				{#if s.data.metadata?.mode}
					<div class="border border-r-0 border-orange-400 py-1 pr-2 pl-2">
						{s.data.metadata.mode}
					</div>
				{/if}
				{#if s.data.metadata?.user}
					<div class="border border-r-0 border-amber-400 py-1 pr-2 pl-2">
						{s.data.metadata.user}
					</div>
				{/if}
			</div>
			<div
				class="absolute top-2.5 right-0 flex translate-x-[calc(100%+1px)] flex-col items-start gap-1.5"
			>
				<button class="bg-rose-400 py-0.5 pr-3.5 pl-2" onclick={() => (showInfo = !showInfo)}>
					{showInfo ? 'Hide' : 'More'} Info
				</button>
				{#each [[s.data.stream, 'Icecast'], [`${new URL('.stream.ogg.m3u', s.data.stream)}`, '.m3u'], [`${new URL('.stream.ogg.xslf', s.data.stream)}`, '.xslf']] as const as [href, name] (href)}
					<a rel="external" {href} class="bg-pink-400 py-0.5 pr-3.5 pl-2">{name}</a>
				{/each}
			</div>
			{#if s.data.metadata?.cover}
				<img alt="cover" src={s.data.metadata.cover} />
			{/if}
			<div class="max-w-full px-2 py-1.5">
				<p class="overflow-hidden font-semibold text-ellipsis whitespace-nowrap">
					{s.data.metadata?.title}
				</p>
				<p class="overflow-hidden text-ellipsis whitespace-nowrap">{s.data.metadata?.artist}</p>
			</div>
			<audio
				controls
				src={new URL('stream.ogg', s.data.stream) +
					'?' +
					new URLSearchParams({ cacheBuster: crypto.randomUUID() })}
				class="min-w-full"
			></audio>
		</section>

		{#if showInfo && s.data.metadata}
			<pre class="absolute top-2 left-2 opacity-50">{JSON.stringify(
					Object.fromEntries(
						Object.entries(s.data.metadata).filter((m) => m[1] && m[1]?.length <= 128)
					),
					null,
					4
				)}</pre>
		{/if}
	{:else if s.type === 'error'}
		<pre>error: {s.reason}</pre>
	{:else if s satisfies never}{/if}
</main>

<style>
	audio::-webkit-media-controls-enclosure {
		border-radius: 0;
	}
</style>
