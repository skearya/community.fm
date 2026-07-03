<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<main class="mx-auto flex max-w-360 flex-col">
	<nav class="flex items-center justify-between px-7.5 py-8">
		<div class="flex gap-x-3.75">
			<img
				src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
				alt="avatar"
				class="size-12.75 rounded-full"
			/>
			<div>
				<p class="text-[22px] leading-6.5 tracking-wide text-[#686868]">DJ</p>
				<div class="flex items-center">
					<p class="text-[22px] leading-6.5 tracking-wide">Skeary</p>
					{@render arrow()}
				</div>
			</div>
		</div>
		<div class="flex items-center gap-x-3">
			<div class="flex gap-x-1.5 rounded-[59px] bg-foreground px-5 py-3.75 text-background">
				{@render person()}
				<p class="text-[22px] leading-6.5 tracking-wide">22 Listeners</p>
			</div>
			<div class="flex gap-x-1.5 rounded-[59px] bg-[#FF393C] px-5 py-3.75 text-background">
				{@render circle()}
				<p class="text-[22px] leading-6.5 tracking-wide">Live</p>
			</div>
			<div class="flex gap-x-1.5 rounded-[59px] bg-[#F2F2F7] px-5 py-3.75 text-background">
				{@render volume()}
			</div>
		</div>
	</nav>

	<div class="flex items-center justify-center gap-x-39.75">
		<section>
			<p class="mb-1.5 text-[48px] leading-14.25 font-medium">Supermodel</p>
			<p class="mb-7.5 text-[32px] leading-9.5 text-[#686868]">SZA</p>
			<img
				src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
				alt="avatar"
				class="size-127.75 rounded-[83px]"
			/>
		</section>

		<section>
			<p class="mb-6 leading-4.75 tracking-[-0.02em] text-[#686868]">Previous songs</p>
			<div class="flex flex-col gap-y-4.25">
				{#each { length: 5 }}
					<div class="flex gap-x-5.5">
						<img
							src="https://f4.bcbits.com/img/a3554352334_1x1_700.avif"
							alt="cover"
							class="size-25.5 rounded-2xl"
						/>
						<div>
							<p class="mb-3 text-[22px] leading-7.5">
								Nothing Even Matters (D’Angelo)
								<br />
								<span class="text-[#686868]">Ms. Lauryn Hill</span>
							</p>
							<div class="flex gap-x-3.25">
								<div class="flex items-center gap-1.25">
									{@render up()}
									<p class="text-[22px] leading-6.5">11</p>
								</div>
								<div class="flex items-center gap-1.25">
									{@render down()}
									<p class="text-[22px] leading-6.5 text-[#AEAEB2]">2</p>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</section>
	</div>

	<div class="mt-24 h-0.5 w-full max-w-332 self-center rounded-[28px] bg-[#F1F1F1]">
		<div class="relative h-0.5 w-2/3 rounded-[28px] bg-[#3A3A3A]">
			<p class="absolute right-0 bottom-2 translate-x-1/2">-2:23</p>
		</div>
	</div>
</main>

{#snippet arrow()}
	<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path d="M6.4 19L5 17.6L14.6 8H6V6H18V18H16V9.4L6.4 19Z" fill="#1F1F1F" />
	</svg>
{/snippet}

{#snippet person()}
	<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M9.82187 11.6781C8.94062 10.7969 8.5 9.7375 8.5 8.5C8.5 7.2625 8.94062 6.20312 9.82187 5.32187C10.7031 4.44062 11.7625 4 13 4C14.2375 4 15.2969 4.44062 16.1781 5.32187C17.0594 6.20312 17.5 7.2625 17.5 8.5C17.5 9.7375 17.0594 10.7969 16.1781 11.6781C15.2969 12.5594 14.2375 13 13 13C11.7625 13 10.7031 12.5594 9.82187 11.6781ZM4 22V18.85C4 18.2125 4.16406 17.6266 4.49219 17.0922C4.82031 16.5578 5.25625 16.15 5.8 15.8687C6.9625 15.2875 8.14375 14.8516 9.34375 14.5609C10.5437 14.2703 11.7625 14.125 13 14.125C14.2375 14.125 15.4562 14.2703 16.6562 14.5609C17.8562 14.8516 19.0375 15.2875 20.2 15.8687C20.7437 16.15 21.1797 16.5578 21.5078 17.0922C21.8359 17.6266 22 18.2125 22 18.85V22H4ZM6.25 19.75H19.75V18.85C19.75 18.6437 19.6984 18.4562 19.5953 18.2875C19.4922 18.1187 19.3562 17.9875 19.1875 17.8937C18.175 17.3875 17.1531 17.0078 16.1219 16.7547C15.0906 16.5016 14.05 16.375 13 16.375C11.95 16.375 10.9094 16.5016 9.87812 16.7547C8.84687 17.0078 7.825 17.3875 6.8125 17.8937C6.64375 17.9875 6.50781 18.1187 6.40469 18.2875C6.30156 18.4562 6.25 18.6437 6.25 18.85V19.75ZM14.5891 10.0891C15.0297 9.64844 15.25 9.11875 15.25 8.5C15.25 7.88125 15.0297 7.35156 14.5891 6.91094C14.1484 6.47031 13.6187 6.25 13 6.25C12.3812 6.25 11.8516 6.47031 11.4109 6.91094C10.9703 7.35156 10.75 7.88125 10.75 8.5C10.75 9.11875 10.9703 9.64844 11.4109 10.0891C11.8516 10.5297 12.3812 10.75 13 10.75C13.6187 10.75 14.1484 10.5297 14.5891 10.0891Z"
			fill="white"
		/>
	</svg>
{/snippet}

{#snippet circle()}
	<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M4.075 19.925C2.025 17.875 1 15.4 1 12.5C1 9.6 2.025 7.125 4.075 5.075C6.125 3.025 8.6 2 11.5 2C14.4 2 16.875 3.025 18.925 5.075C20.975 7.125 22 9.6 22 12.5C22 15.4 20.975 17.875 18.925 19.925C16.875 21.975 14.4 23 11.5 23C8.6 23 6.125 21.975 4.075 19.925ZM16.8063 17.8063C18.2688 16.3438 19 14.575 19 12.5C19 10.425 18.2688 8.65625 16.8063 7.19375C15.3438 5.73125 13.575 5 11.5 5C9.425 5 7.65625 5.73125 6.19375 7.19375C4.73125 8.65625 4 10.425 4 12.5C4 14.575 4.73125 16.3438 6.19375 17.8063C7.65625 19.2688 9.425 20 11.5 20C13.575 20 15.3438 19.2688 16.8063 17.8063Z"
			fill="white"
		/>
	</svg>
{/snippet}

{#snippet volume()}
	<svg width="26" height="24" viewBox="0 0 26 24" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M15.8889 24V21.1886C18.0556 20.5943 19.8009 19.4514 21.125 17.76C22.4491 16.0686 23.1111 14.1486 23.1111 12C23.1111 9.85143 22.4491 7.93143 21.125 6.24C19.8009 4.54857 18.0556 3.40571 15.8889 2.81143V0C18.8741 0.64 21.3056 2.07429 23.1833 4.30286C25.0611 6.53143 26 9.09714 26 12C26 14.9029 25.0611 17.4686 23.1833 19.6971C21.3056 21.9257 18.8741 23.36 15.8889 24ZM0 16.1486V7.92H5.77778L13 1.06286V23.0057L5.77778 16.1486H0ZM15.8889 17.52V6.48C17.0204 6.98286 17.9051 7.73714 18.5431 8.74286C19.181 9.74857 19.5 10.8457 19.5 12.0343C19.5 13.2 19.181 14.28 18.5431 15.2743C17.9051 16.2686 17.0204 17.0171 15.8889 17.52ZM10.1111 7.71429L7.00556 10.6629H2.88889V13.4057H7.00556L10.1111 16.3543V7.71429Z"
			fill="#1F1F1F"
		/>
	</svg>
{/snippet}

{#snippet up()}
	<svg width="22" height="11" viewBox="0 0 22 11" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path d="M0 11L11 0L22 11H0Z" fill="#34C759" />
	</svg>
{/snippet}

{#snippet down()}
	<svg width="22" height="11" viewBox="0 0 22 11" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path d="M22 0L11 11L9.61651e-07 -1.9233e-06L22 0Z" fill="#AEAEB2" />
	</svg>
{/snippet}
