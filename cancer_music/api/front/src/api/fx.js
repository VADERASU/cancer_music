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

const applyFilter_ = (id, staffEntry) => {
    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = `url(#${id}_filter)`;
            svg.setAttribute('filter', filter);
        })
    );
};

export const applyFilter = (val) => curry(applyFilter_)(val);

export const blur = (val, id) => {
    const f = document.querySelector(`#${id}_blur`);
    f.setAttribute('stdDeviation', val);
};

export const erode = (val, id) => {
    const f = document.querySelector(`#${id}_erode`);
    f.setAttribute('radius', `${val} ${val}`);
};

export const shadow = (val, id) => {
    const f = document.querySelector(`#${id}_shadow`);
    f.setAttribute('dx', `${val}`);
    f.setAttribute('dy', `${val}`);
};

export const shadowColor = (val, id) => {
    const f = document.querySelector(`#${id}_shadow`);
    f.setAttribute('flood-color', val);
};

export const waves = (val, id) => {
    const f = document.querySelector(`#${id}_displacement`);
    f.setAttribute('scale', `${val}`);
};
