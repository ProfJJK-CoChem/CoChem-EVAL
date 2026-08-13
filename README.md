# CoChem-EVAL

**PI / Lead Developer**: Dr. Joshua John Klaassen  
**ORCiD**: [https://orcid.org/0009-0007-1506-4401](https://orcid.org/0009-0007-1506-4401)  
**CoChem GitHub Organization**: [https://github.com/ProfJJK-CoChem](https://github.com/ProfJJK-CoChem)  

### Authoritative Documentation
* [CoChem User Manual](https://github.com/ProfJJK-CoChem/CoChem-BASE/blob/main/CoChem_User_Manual.md)
* [CoChem Method Matrix](https://github.com/ProfJJK-CoChem/CoChem-BASE/blob/main/Method_Matrix.md)

---

## 1. Overview
CoChem-EVAL provides high-level evaluation pipelines for chemical properties, reaction energies, and spectroscopic data. Designed to produce publication-grade outputs, it strictly compiles energies, geometries, and metadata into standardized QCSchema JSONs and directly outputs SI-ready artifacts (e.g., LaTeX and Markdown).

## 2. Recent Updates
> **NOTICE**: In alignment with the CoChem ecosystem, this module now relies heavily on the **Valeev Stack (MPQC, F12)**. Output parsers and evaluation tools have been calibrated to extract F12 explicitly correlated energies seamlessly, resulting in sub-chemical accuracy evaluations that are 4x faster `[E]` than traditional basis set extrapolation approaches.

## 3. Installation
