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
