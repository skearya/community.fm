<script lang="ts">
	import type { PageProps } from './$types';
	import type { Data, Message } from '$lib/types';
	import { onMount } from 'svelte';
	import Player from '$lib/components/Player.svelte';
	import { unreachable, wait } from '$lib/utils';
	import { fade } from 'svelte/transition';

	let { data }: PageProps = $props();

	type Connection =
		| { type: 'awaiting' }
		| { type: 'connected' }
		| { type: 'ready'; data: Data }
		| { type: 'error'; reason: string };

	let connection = $state<Connection>({ type: 'awaiting' });

	onMount(() => {
		const eventSource = new EventSource('/api/subscribe');

		eventSource.addEventListener('open', () => {
			connection = { type: 'connected' };
		});

		eventSource.addEventListener('message', (event) => {
			const message = JSON.parse(event.data) as Message;

			switch (message.type) {
				case 'info':
					connection = { type: 'ready', data: message };
					break;
				case 'metadata':
					if (connection.type !== 'ready') throw new Error();

					connection.data.metadata = message.metadata;
					break;
				case 'status':
					if (connection.type !== 'ready') throw new Error();

					connection.data.status = message.status;
					break;
				default:
					message satisfies never;
			}
		});

		eventSource.addEventListener('error', (event) => {
			console.error('Connection failed', event);
			connection = { type: 'error', reason: `${eventSource.readyState}` };
		});
	});
</script>

{#if connection.type === 'awaiting' || connection.type === 'connected'}
	{#await wait(300) then}
		{@render message('Loading...')}
	{/await}
{:else if connection.type === 'ready'}
	<Player {...connection.data} />
{:else if connection.type === 'error'}
	{@render message(`Error: ${connection.reason}`)}
{:else if connection satisfies never}
	{unreachable(connection)}
{/if}

{#snippet message(text: string)}
	<main
		transition:fade={{ duration: 125 }}
		class="flex h-screen items-center justify-center text-lg"
	>
		<p>{text}</p>
	</main>
{/snippet}
