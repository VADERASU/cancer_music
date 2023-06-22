import { curry } from './utils';

const _colorNotes = (color, staffEntry) => {
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            const svg = n.vfnote[0].attrs.el;
            for (const child of svg.getElementsByTagName('path')) {
                child.setAttribute("stroke", color);
                child.setAttribute("fill", color);
            }
        }
    }
};

export const colorNotes = (color) => curry(_colorNotes)(color);

const _modifyAlpha = (alpha, staffEntry) => {
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            const svg = n.vfnote[0].attrs.el;
            svg.setAttribute("opacity", alpha);
        }
    }
};

export const modifyAlpha = (alpha) => curry(_modifyAlpha)(alpha);

const _modifySize = (size, staffEntry) => {
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            const svg = n.vfnote[0].attrs.el;
            const bBox = n.vfnote[0].getBoundingBox();
            for (const child of svg.getElementsByTagName('path')) {
                child.setAttribute("stroke-width", `${size}px`);
            }
        }
    }
};

export const modifySize = (size) => curry(_modifySize)(size);

const _modifyAngle = (angle, staffEntry) => {
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            const svg = n.vfnote[0].attrs.el;
            const bBox = n.vfnote[0].getBoundingBox();
            const { x, y, w, h } = bBox;
            const t = `rotate(${angle},${x + (w / 2)}, ${y + (h / 2)})`;
            if (n.sourceNote.isRestFlag) {
                svg.setAttribute("transform", t);
            } else {
                const stem = svg.querySelector('.vf-stem');
                if (stem) {
                    stem.setAttribute("transform", t);
                }
            }
        }
    }
};

export const modifyAngle = (angle) => curry(_modifyAngle)(angle);

export const initFilters = (svg) => {
    const defs = document.createElementNS('http://www.w3.org/2000/svg', "defs");
    const blur = document.createElementNS('http://www.w3.org/2000/svg', "filter");
    blur.id = 'blur';
    const blurfx = document.createElementNS('http://www.w3.org/2000/svg', "feGaussianBlur");
    blurfx.setAttribute('stdDeviation', 2);
    blur.appendChild(blurfx);
    defs.appendChild(blur);
    svg.appendChild(defs);
};

export const _blur = (val, staffEntry) => {
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            const svg = n.vfnote[0].attrs.el;
            const filter = (val) ? 'url(#blur)' : '';
            svg.setAttribute('filter', filter);
        }
    }
};

export const blur = (val) => curry(_blur)(val);
