import { curry } from './utils';

const _colorNotes = (color, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const paths = Array.from(svg.getElementsByTagName('path'));
            paths.forEach((child) => {
                child.setAttribute("stroke", color);
                child.setAttribute("fill", color);
            })
        })
    )
};

export const colorNotes = (color) => curry(_colorNotes)(color);

const _modifyAlpha = (alpha, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            svg.setAttribute("opacity", alpha);
        })
    )
};

export const modifyAlpha = (alpha) => curry(_modifyAlpha)(alpha);

const _modifySize = (size, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const paths = Array.from(svg.getElementsByTagName('path'));
            paths.forEach((child) => child.setAttribute("stroke-width", `${size}px`));
        })
    );
};

export const modifySize = (size) => curry(_modifySize)(size);

const _modifyAngle = (angle, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const bBox = n.vfnote[0].getBoundingBox();
            const { x, y, w, h } = bBox;
            const t = `rotate(${angle},${x + (w / 2)}, ${y + (h / 2)})`;
            // can store transforms in notes!
            // n.transform = t;
            if (n.sourceNote.isRestFlag) {
                svg.setAttribute("transform", t);
            } else {
                const stem = svg.querySelector('.vf-stem');
                if (stem) {
                    stem.setAttribute("transform", t);
                }
            }
        }));
};

export const modifyAngle = (angle) => curry(_modifyAngle)(angle);

export const initFilters = (svg) => {
    const defs = document.createElementNS('http://www.w3.org/2000/svg', "defs");

    const blur = document.createElementNS('http://www.w3.org/2000/svg', "filter");
    blur.id = 'blur';
    const blurfx = document.createElementNS('http://www.w3.org/2000/svg', "feGaussianBlur");
    blurfx.setAttribute('stdDeviation', "2");
    blur.appendChild(blurfx);
    defs.appendChild(blur);

    const erosion = document.createElementNS('http://www.w3.org/2000/svg', "filter");
    erosion.id = 'erode';
    erosion.setAttribute('x', '-20%');
    erosion.setAttribute('y', '-20%');
    erosion.setAttribute('width', '140%');
    erosion.setAttribute('height', '140%');
    erosion.setAttribute('filterUnits', 'objectBoundingBox');
    erosion.setAttribute('primitiveUnits', 'userSpaceOnUse');

    const erosionfx = document.createElementNS('http://www.w3.org/2000/svg', "feMorphology");
    erosionfx.setAttribute('operator', "erode");
    erosionfx.setAttribute('radius', '1 1');
    erosionfx.setAttribute('in', 'SourceGraphic');
    erosionfx.setAttribute('x', '0%');
    erosionfx.setAttribute('y', '0%');
    erosionfx.setAttribute('width', '100%');
    erosionfx.setAttribute('height', '100%');
    erosionfx.setAttribute('result', 'morphology');

    erosion.appendChild(erosionfx);
    defs.appendChild(erosion);

    svg.appendChild(defs);
};

const _blur = (val, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = (val) ? 'url(#blur)' : '';
            svg.setAttribute('filter', filter);
        })
    );
};

export const blur = (val) => curry(_blur)(val);

const _erode = (val, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = (val) ? 'url(#erode)' : '';
            svg.setAttribute('filter', filter);
        })
    );
};

export const erode = (val) => curry(_erode)(val);
