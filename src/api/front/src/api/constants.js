/* eslint-disable */
export const API_URL = (import.meta.env.PROD) ? '' : 'http://localhost:8000';
/* eslint-enable */

// which notes to apply mutations to
export const mutationMarkers = {
    "insertion": "i",
    "deletion": "d",
    "transposition": "t",
    "translocation": "tl",
    "inversion": "iv",
    "cure": "c"
};
