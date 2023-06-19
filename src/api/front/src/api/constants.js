export const API_URL = (import.meta.env.MODE == 'development') ? 'http://localhost:8000' : '';

// which notes to apply mutations to
// TODO: either have some mean full measures or just add lyrics to all for stuff like
// transposition
export const mutationMarkers = {
    "insertion": "i",
    "deletion": "d",
    "transposition": "t",
    "translocation": "tl",
    "inversion": "iv",
};

