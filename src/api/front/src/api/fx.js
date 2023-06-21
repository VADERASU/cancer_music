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
            const { x, y, w, h } = bBox;
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
            svg.setAttribute("transform", `rotate(${angle},${x + (w / 2)}, ${y + (h / 2)})`);
        }
    }
};

export const modifyAngle = (angle) => curry(_modifyAngle)(angle);
