import { MXLHelper, IXmlElement, MusicSheetReader, GraphicalMusicSheet, VexFlowMusicSheetCalculator, EngravingRules } from "opensheetmusicdisplay";
import * as zip from "@zip.js/zip.js";

// graciously stolen from opensheetmusicdisplay
// https://github.com/opensheetmusicdisplay
/* eslint-disable */

export const mxlToString = (file) => {
    if (file.name.endsWith(".mxl")) {
        const reader = new zip.ZipReader(new zip.BlobReader(file));
        return reader.getEntries().then((entries) => {
            const texts = entries.
                filter((e) => e.filename.endsWith(".xml") && e.filename !== "META-INF/container.xml").
                map((e) => e.getData(new zip.TextWriter()).then((res) => res));
            if (texts.length != 1) {
                return Promise.reject(new Error("MXL file which was provided is invalid."));
            } else {
                return texts[0];
            }
        })
    } else {
        return file.text();
    }
};

export const parseMXL = (content, tempTitle = "Untitled Score") => {
    // Warning! This function is asynchronous! No error handling is done here.
    // console.log("typeof content: " + typeof content);
    if (typeof content === "string") {
        const str = content;
        // console.log("substring: " + str.substr(0, 5));
        if (str.substr(0, 4) === "\x50\x4b\x03\x04") {
            // This is a zip file, unpack it first
            return MXLHelper.MXLtoXMLstring(str).then(
                (x) => parseMXL(x),
                (err) => {
                    console.log(err);
                    throw new Error("OpenSheetMusicDisplay: Invalid MXL file");
                }
            );
        }
        // Javascript loads strings as utf-16, which is wonderful BS if you want to parse UTF-8 :S
        if (str.substr(0, 3) === "\uf7ef\uf7bb\uf7bf") {
            // UTF with BOM detected, truncate first three bytes and pass along
            return parseMXL(str.substr(3));
        }
        let trimmedStr = str;
        if (/^\s/.test(trimmedStr)) { // only trim if we need to. (end of string is irrelevant)
            trimmedStr = trimmedStr.trim(); // trim away empty lines at beginning etc
        }
        if (trimmedStr.substr(0, 6).includes("<?xml")) { // first character is sometimes null, making first five characters '<?xm'.
            // Parse the string representing an xml file
            const parser = new DOMParser();
            content = parser.parseFromString(trimmedStr, "application/xml");
        } else {
            console.error("[OSMD] osmd.load(string): Could not process string. Did not find <?xml at beginning.");
        }
    }

    if (!content || !(content).nodeName) {
        return Promise.reject(new Error("OpenSheetMusicDisplay: The document which was provided is invalid"));
    }
    const xmlDocument = (content);
    const xmlDocumentNodes = xmlDocument.childNodes;

    let scorePartwiseElement;
    for (let i = 0, { length } = xmlDocumentNodes; i < length; i += 1) {
        const node = xmlDocumentNodes[i];
        if (node.nodeType === Node.ELEMENT_NODE && node.nodeName.toLowerCase() === "score-partwise") {
            scorePartwiseElement = node;
            break;
        }
    }
    console.log(scorePartwiseElement);
    if (!scorePartwiseElement) {
        console.error("Could not parse MusicXML, no valid partwise element found");
        return Promise.reject(new Error("OpenSheetMusicDisplay: Document is not a valid 'partwise' MusicXML"));
    }
    const score = new IXmlElement(scorePartwiseElement);
    const reader = new MusicSheetReader(undefined);
    const sheet = reader.createMusicSheet(score, tempTitle);
    if (sheet === undefined) {
        // error loading sheet, probably already logged, do nothing
        return Promise.reject(new Error("given music sheet was incomplete or could not be loaded."));
    }
    // apparently more information is captured by the calculator but not caught by the reader..
    const calc = new VexFlowMusicSheetCalculator(new EngravingRules());
    const graphic = new GraphicalMusicSheet(sheet, calc);
    console.log(graphic);
    // if (this.sheet.TitleString === "osmd.Version") {
    //     this.sheet.TitleString = "OSMD version: " + this.Version; // useful for debug e.g. when console not available
    // }
    return Promise.resolve(sheet);
}
