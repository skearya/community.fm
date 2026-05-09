<script lang="ts">
	type Info = {
		modes: string[];
		stream: string;
		metadata: Record<string, string> | null;
	};

	async function fetchInfo() {
		const res = await fetch('/api/info');
		const json = await res.json();

		return json as Info;
	}
</script>

{#await fetchInfo()}
	<pre>loading</pre>
{:then info}
	<audio
		controls
		src={new URL('stream.ogg', info.stream) +
			'?' +
			new URLSearchParams({ random: crypto.randomUUID() })}
	></audio>
	<img alt="cover" src={info.metadata?.cover} />
	<pre>{JSON.stringify(info, null, 2)}</pre>
{/await}
