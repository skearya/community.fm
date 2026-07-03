// Based on `flip` from 'svelte/animate'
export function flip(
	node: Element,
	{ from, to }: { from: DOMRect; to: DOMRect },
	params: {
		delay?: number;
		duration?: number;
		easing?: string;
	} = {}
): Animation {
	const { delay = 0, duration = 300, easing = 'ease-out' } = params;

	const style = getComputedStyle(node);

	// find the transform origin, expressed as a pair of values between 0 and 1
	const transform = style.transform === 'none' ? '' : style.transform;
	let [ox, oy] = style.transformOrigin.split(' ').map(parseFloat);
	ox /= node.clientWidth;
	oy /= node.clientHeight;

	// calculate effect of parent transforms and zoom
	const zoom = getZoom(node); // https://drafts.csswg.org/css-viewport/#effective-zoom
	const sx = node.clientWidth / to.width / zoom;
	const sy = node.clientHeight / to.height / zoom;

	// find the starting position of the transform origin
	const fx = from.left + from.width * ox;
	const fy = from.top + from.height * oy;

	// find the ending position of the transform origin
	const tx = to.left + to.width * ox;
	const ty = to.top + to.height * oy;

	// find the translation at the start of the transform
	const dx = (fx - tx) * sx;
	const dy = (fy - ty) * sy;

	// find the relative scale at the start of the transform
	const dsx = from.width / to.width;
	const dsy = from.height / to.height;

	return node.animate(
		{
			transform: [
				`${transform} translate(${dx}px, ${dy}px) scale(${dsx}, ${dsy})`,
				`${transform} translate(0px, 0px) scale(1, 1)`
			]
		},
		{
			delay,
			duration,
			easing
		}
	);
}

function getZoom(element: Element) {
	if ('currentCSSZoom' in element) {
		return element.currentCSSZoom;
	}

	let current: Element | null = element;
	let zoom = 1;

	while (current !== null) {
		zoom *= +getComputedStyle(current).zoom;
		current = current.parentElement as Element | null;
	}

	return zoom;
}

export function cloneOver(node: HTMLElement, rect: DOMRect): HTMLElement {
	const clone = node.cloneNode(true) as HTMLElement;

	clone.style.position = 'fixed';
	clone.style.left = `${rect.left}px`;
	clone.style.top = `${rect.top}px`;
	clone.style.width = `${rect.width}px`;
	clone.style.height = `${rect.height}px`;
	clone.style.margin = '0';
	clone.style.zIndex = '1';
	clone.style.pointerEvents = 'none';

	document.body.appendChild(clone);

	return clone;
}
