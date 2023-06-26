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

export const initFilter = (id) => {
    const filter = document.createElementNS('http://www.w3.org/2000/svg', "filter");
    filter.id = `${id}_filter`;
    filter.setAttribute('filterUnits', 'objectBoundingBox');
    filter.setAttribute('primitiveUnits', 'userSpaceOnUse');

    const blurfx = document.createElementNS('http://www.w3.org/2000/svg', "feGaussianBlur");
    blurfx.id = `${id}_blur`;
    blurfx.setAttribute('stdDeviation', "0");
    blurfx.setAttribute('result', 'blurred');
    filter.appendChild(blurfx);

    const erosionfx = document.createElementNS('http://www.w3.org/2000/svg', "feMorphology");
    erosionfx.id = `${id}_erode`;
    erosionfx.setAttribute('operator', "erode");
    erosionfx.setAttribute('radius', '0 0');
    erosionfx.setAttribute('in', 'blurred');
    erosionfx.setAttribute('result', 'morphology');
    filter.appendChild(erosionfx);

    const shadow = document.createElementNS('http://www.w3.org/2000/svg', "feDropShadow");
    shadow.id = `${id}_shadow`;
    shadow.setAttribute('stdDeviation', '1 1');
    shadow.setAttribute('dx', '0');
    shadow.setAttribute('dy', '0');
    shadow.setAttribute('in', 'morphology');
    shadow.setAttribute('result', 'shadow');
    filter.appendChild(shadow);

    const defs = document.querySelector('#defs');
    defs.append(filter);
}

export const initDefs = (svg) => {
    const defs = document.createElementNS('http://www.w3.org/2000/svg', "defs");
    defs.id = 'defs'
    svg.appendChild(defs);
};

const _blur = ({ val, id }, staffEntry) => {
    const blur = document.querySelector(`#${id}_blur`);
    blur.setAttribute('stdDeviation', val);

    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = `url(#${id}_filter)`;
            svg.setAttribute('filter', filter);
        })
    );
};

export const blur = (val) => curry(_blur)(val);

// can move this? erode can be changed elsewhere
// just apply filter accordingly?
const _erode = ({ val, id }, staffEntry) => {
    const erode = document.querySelector(`#${id}_erode`);
    erode.setAttribute('radius', `${val} ${val}`);

    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = `url(#${id}_filter)`;
            svg.setAttribute('filter', filter);
        })
    );
};

export const erode = (val) => curry(_erode)(val);

const _shadow = ({ val, id }, staffEntry) => {
    const f = document.querySelector(`#${id}_shadow`);
    f.setAttribute('dx', `${val}`);
    f.setAttribute('dy', `${val}`);

    staffEntry.graphicalVoiceEntries.forEach((g) =>
        g.notes.forEach((n) => {
            const svg = n.getSVGGElement();
            const filter = `url(#${id}_filter)`;
            svg.setAttribute('filter', filter);
        })
    );
};

export const shadow = (val) => curry(_shadow)(val);
