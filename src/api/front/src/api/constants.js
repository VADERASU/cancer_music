export const API_URL = (import.meta.env.MODE == 'development') ? 'http://localhost:8000' : '';

// which notes to apply mutations to
export const mutationMarkers = {
    "insertion": "i",
    "deletion": "d",
    "transposition": "t",
    "translocation": "tl",
    "inversion": "iv",
};
