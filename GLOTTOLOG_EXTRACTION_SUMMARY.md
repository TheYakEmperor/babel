# Glottolog Language Family Tree Extraction

## Summary

Successfully extracted the complete Glottolog language family tree structure and created a comprehensive folder hierarchy.

## Results

- **Total Languages/Families Created**: 27,034 folders
- **Data Source**: Glottolog 5.2 (https://glottolog.org)
- **Output Location**: `/languages/` directory
- **Creation Date**: January 12, 2026

## Structure

The folder structure follows the genealogical classification from Glottolog:

```
languages/
├── indo-european/
│   ├── anatolian/
│   │   ├── hittite/
│   │   └── luvo-lydian/
│   │       ├── luvo-palaic/
│   │       │   ├── luvic/
│   │       │   │   ├── luvian/
│   │       │   │   └── ...
│   │       │   └── palaic/
│   │       └── lydian/
│   ├── balkan/
│   │   ├── albanian/
│   │   ├── armenic/
│   │   └── ...
│   ├── celtic/
│   ├── germanic/
│   ├── indo-iranian/
│   ├── italic/
│   ├── slavic/
│   └── tocharian/
├── sino-tibetan/
├── afro-asiatic/
├── austronesian/
└── ... (and 427 more top-level families)
```

## Data Characteristics

- **Folder naming**: Lowercase, hyphens for spaces, special characters removed
- **Hierarchical depth**: Varies by language family (up to 15+ levels for some families)
- **Coverage**: All languoids including families, languages, and dialects

## Files

- `languoid.csv` - Source data file from Glottolog (27,035 rows including header)
- `extract_glottolog.py` - Python script that created the folder structure
- This summary document

## Usage

Each folder represents a languoid in the Glottolog system. You can use this structure to:

1. Organize linguistic data by language family
2. Create index pages for each language
3. Build a comprehensive language documentation website
4. Map linguistic relationships visually

## Notes

- The structure is based on Glottolog's genealogical classification
- Folder names are automatically generated from Glottolog language names
- Total folder count (27,034) = number of unique languoids in Glottolog 5.2
- No errors occurred during folder creation

## References

- Glottolog: https://glottolog.org
- Citation: Hammarström, Harald & Forkel, Robert & Haspelmath, Martin & Bank, Sebastian. 2025. Glottolog 5.2. Leipzig: Max Planck Institute for Evolutionary Anthropology. https://doi.org/10.5281/zenodo.15525265
