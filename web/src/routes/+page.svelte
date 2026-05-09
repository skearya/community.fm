<script lang="ts">
	import { onMount } from 'svelte';

	type Data = {
		stream: string;
		metadata: Record<string, string> | null;
		modes: string[];
	};

	type State =
		| { type: 'awaiting' }
		| { type: 'connected' }
		| { type: 'ready'; data: Data }
		| { type: 'error'; reason: string };

	type Message = ({ type: 'info' } & Data) | { type: 'metadata'; metadata: Data['metadata'] };

	let state = $state<State>({ type: 'awaiting' });

	onMount(() => {
		const eventSource = new EventSource('/api/subscribe');

		eventSource.addEventListener('open', () => {
			state = { type: 'connected' };
		});

		eventSource.addEventListener('message', (event) => {
			const message = JSON.parse(event.data) as Message;

			switch (message.type) {
				case 'info':
					state = { type: 'ready', data: message };
					break;
				case 'metadata':
					if (state.type !== 'ready') throw new Error();

					state.data.metadata = message.metadata;
					break;
			}
		});

		eventSource.addEventListener('error', (event) => {
			console.error('Connection failed', event);
			state = { type: 'error', reason: `${eventSource.readyState}` };
		});
	});
</script>

{#if state.type === 'awaiting'}
	<pre>connecting</pre>
{:else if state.type === 'connected'}
	<pre>connected</pre>
{:else if state.type === 'ready'}
	<audio
		controls
		autoplay
		src={new URL('stream.ogg', state.data.stream) +
			'?' +
			new URLSearchParams({ cacheBuster: crypto.randomUUID() })}
	></audio>
	<img alt="cover" src={state.data.metadata?.cover} class="max-h-64 max-w-64" />
	<pre>{JSON.stringify(state.data, null, 2)}</pre>
{:else if state.type === 'error'}
	<pre>error {state.reason}</pre>
{:else if state satisfies never}{/if}
