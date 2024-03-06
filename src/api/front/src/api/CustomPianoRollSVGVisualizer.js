import {
    BaseSVGVisualizer
} from "@magenta/music";
import { StaffModel } from "staffrender";
import {
    hexToRgbA
} from "./utils";


export default class CustomPianoRollSVGVisualizer extends BaseSVGVisualizer {
    staffModel;

    constructor(
        sequence, svg,
        config = {}) {
        super(sequence, config);

        if (!(svg instanceof SVGSVGElement)) {
            throw new Error(
                'This visualizer requires an <svg> element to display the visualization');
        }
        this.svg = svg;
        this.parentElement = svg.parentElement;

        const size = this.getSize();
        this.width = size.width;
        this.height = size.height;

        // Make sure that if we've used this svg element before, it's now emptied.
        this.svg.style.width = `${this.width}px`;
        this.svg.style.height = `${this.height}px`;

        this.clear();
        this.staffModel = new StaffModel(this.getScoreInfo(sequence), 0);
        this.draw();
    }

    draw() {
        this.noteSequence.notes.forEach((note, i) => {
            const size = this.getNotePosition(note, i);
            const fill = this.getNoteFillColor(note, false);
            const dataAttributes = [
                ['index', i],
                ['instrument', note.instrument],
                ['program', note.program],
                ['isDrum', note.isDrum === true],
                ['pitch', note.pitch],
            ];
            const cssProperties = [
                ['--midi-velocity',
                    String(note.velocity !== undefined ? note.velocity : 127)]
            ];

            this.drawNote(size.x, size.y, size.w, size.h, fill,
                dataAttributes, cssProperties);
        });

        this.staffModel.staffBlockMap.forEach((staffBlock, quarters) => {
            const barNum = staffBlock.barNumber; 
            const x =  this.staffModel.barsInfo.quartersToTime(quarters) * this.config.pixelsPerTimeStep;
            if (barNum === Math.trunc(barNum)) {
                const bar = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                bar.setAttribute('fill', 'black');
                bar.setAttribute('x', `${x}`);
                bar.setAttribute('y', '0');
                bar.setAttribute('width', '1');
                bar.setAttribute('height', `${this.height}`);
                this.svg.appendChild(bar);
            }
        });
        this.drawn = true;
    }

    getNoteFillColor(note, isActive) {
        const opacityBaseline = 0.2;  // Shift all the opacities up a little.
        const opacity = note.velocity ? note.velocity / 100 + opacityBaseline : 1;
        const colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928'];

        const fill =
            `rgba(${isActive ? this.config.activeNoteRGB : hexToRgbA(colors[note.pitch % 12])}, ${opacity})`;
        return fill;
    }

    drawNote(
        x, y, w, h, fill,
        dataAttributes, cssProperties) {
        if (!this.svg) {
            return;
        }
        const rect =
            document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.classList.add('note');
        rect.setAttribute('fill', fill);

        // Round values to the nearest integer to avoid partially filled pixels.
        rect.setAttribute('x', `${Math.round(x)}`);
        rect.setAttribute('y', `${Math.round(y)}`);
        rect.setAttribute('width', `${Math.round(w)}`);
        rect.setAttribute('height', `${Math.round(h)}`);
        dataAttributes.forEach(([key, value]) => {
            if (value !== undefined) {
                rect.dataset[key] = `${value}`;
            }
        });
        cssProperties.forEach(([key, value]) => {
            rect.style.setProperty(key, value);
        });
        this.svg.appendChild(rect);
    }

    drawOutline() {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('fill', 'none');
        rect.setAttribute('stroke', 'black');
        rect.setAttribute('x', '0');
        rect.setAttribute('y', '0');
        rect.setAttribute('width', `${this.width}`)
        rect.setAttribute('height', `${this.height}`);
    }

    timeToQuarters(time) {
        const q = time * this.noteSequence.tempos[0].qpm / 60;
        return Math.round(q * 16) / 16;  // Current resolution = 1/16 quarter.
    }

    drawStaff() {
        for (let p = this.config.minPitch; p <= this.config.maxPitch; p += 1) {
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            const y = this.height - ((p - this.config.minPitch) * this.config.noteHeight);
            rect.setAttribute('fill', 'none');
            rect.setAttribute('stroke', 'black');
            rect.setAttribute('x', '0');
            rect.setAttribute('y', `${y}`);
            rect.setAttribute('width', `${this.width}`)
            rect.setAttribute('height', `${this.config.noteHeight}`);
            this.svg.appendChild(rect);
        }
    }

    getNoteInfo(note) {
        const startQ =
            this.timeToQuarters(note.startTime);
        const endQ =
            this.timeToQuarters(note.endTime);
        return {
            start: startQ,
            length: endQ - startQ,
            pitch: note.pitch,
            intensity: note.velocity
        };
    }

    getScoreInfo(sequence) {
        const notesInfo = sequence.notes.map((note) =>
            this.getNoteInfo(note)
        );
        return {
            notes: notesInfo,
            tempos: sequence.tempos ?
                sequence.tempos.map((t) => ({ start: this.timeToQuarters(t.time), qpm: t.qpm })) : [],
            keySignatures: sequence.keySignatures ?
                sequence.keySignatures.map((ks) => ({ start: this.timeToQuarters(ks.time), key: ks.key })) : [],
            timeSignatures: sequence.timeSignatures ?
                sequence.timeSignatures.map((ts) => ({
                    start: this.timeToQuarters(ts.time),
                    numerator: ts.numerator,
                    denominator: ts.denominator
                })) : []
        };
    }

}
