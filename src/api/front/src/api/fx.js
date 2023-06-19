import { curry } from './utils.js';
const _colorNotes = (color, staffEntry) => {
    console.log(color, staffEntry);
    for (const g of staffEntry.graphicalVoiceEntries) {
        for (const n of g.notes) {
            n.sourceNote.noteheadColor = color;
        }
    }
};

export const colorNotes = (color) => curry(_colorNotes)(color);
