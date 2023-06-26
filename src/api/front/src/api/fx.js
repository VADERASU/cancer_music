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

    // turbulence + displacementMap work together to create the waves effect
    const turbulence = document.createElementNS('http://www.w3.org/2000/svg', "feTurbulence");
    turbulence.id = `${id}_turbulence`;
    turbulence.setAttribute('baseFrequency', `0.1 0.05`);
    turbulence.setAttribute('numOctaves', '2');
    turbulence.setAttribute('seed', '2');
    turbulence.setAttribute('result', 'turbulence');
    filter.appendChild(turbulence);

    const displacement = document.createElementNS('http://www.w3.org/2000/svg', "feDisplacementMap");
    displacement.id = `${id}_displacement`;
    displacement.setAttribute('in', 'shadow');
    displacement.setAttribute('in2', 'turbulence');
    displacement.setAttribute('scale', '0');
    displacement.setAttribute('xChannelSelector', 'G');
    displacement.setAttribute('yChannelSelector', 'A');
    displacement.setAttribute('result', 'dp');
    filter.appendChild(displacement);

    const defs = document.querySelector('#defs');
    defs.append(filter);
}

export const initDefs = (svg) => {
    const defs = document.createElementNS('http://www.w3.org/2000/svg', "defs");
    defs.id = 'defs'
    svg.appendChild(defs);
};

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


export const waves = (val, id) => {
    const f = document.querySelector(`#${id}_displacement`);
    f.setAttribute('scale', `${val}`);
};
