<script lang="ts">
	import { goto, preloadData, pushState } from '$app/navigation';
	import { page } from '$app/stores';
	import DetailView from '$lib/components/DetailView/DetailView.svelte';
	import { m } from '$paraglide/messages';
	import AuditTableMode from '../../../(third-party)/compliance-assessments/[id=uuid]/table-mode/+page.svelte';
	import TreeView from '$lib/components/TreeView/TreeView.svelte';
	import TreeViewItem from '$lib/components/TreeView/TreeViewItem.svelte';
	import type { Actions, PageData } from './$types';

	interface Props {
		data: PageData;
		form: Actions;
	}

	let { data, form }: Props = $props();

	const mailing =
		Boolean(data.data.compliance_assessment) && Boolean(data.data.representatives.length);
</script>

<div class="flex flex-col space-y-4 whitespace-pre-line">
	<DetailView {data} {mailing} />
	{#if data.data.compliance_assessment}
		<div class="card px-6 py-4 bg-white flex flex-row justify-between shadow-lg w-full">
			<TreeView>
				<TreeViewItem
					alwaysDisplayCaret={true}
					caretOpen=""
					caretClosed="-rotate-90"
					onToggle={async () => {
						const href = `/compliance-assessments/${data.data.compliance_assessment.id}/table-mode`;
						const result = await preloadData(href);
						if (result.type === 'loaded' && result.status === 200) {
							pushState('', { auditTableMode: result.data });
						} else {
							// Something went wrong, try navigating
							goto(href);
						}
					}}
				>
					<span class="font-semibold text-lg select-none">{m.questionnaire()}</span>
					{#snippet childrenSlot()}
						{#if Object.hasOwn($page?.state, 'auditTableMode')}
							<div class="max-h-192 overflow-y-scroll">
								<AuditTableMode
									{form}
									data={$page?.state?.auditTableMode}
									actionPath={`/compliance-assessments/${data.data.compliance_assessment.id}/table-mode`}
									shallow
									questionnaireOnly
									invalidateAll={false}
								/>
							</div>
						{/if}
					{/snippet}
				</TreeViewItem>
			</TreeView>
		</div>
	{/if}
</div>
