[![CASE-Implementation-PyPI-Exifread](https://github.com/casework/CASE-Implementation-PyPI-Exifread/actions/workflows/python-package.yml/badge.svg)](https://github.com/casework/CASE-Implementation-PyPI-Exifread/actions/workflows/python-package.yml)
![CASE Version](https://img.shields.io/badge/CASE%20Version-1.3.0-brightgreen)

# CASE-Implementation-PyPI-Exifread

A repository for the development of an [Exifread](https://pypi.org/project/Exifread/) to [CASE](https://caseontology.org) implementation.

# Usage
> Use of a python virtual environment suggested

```cd CASE-Implementation-PyPI-Exifread```

```pip install .```

```exifread2case <nameof.jpeg>```


# Development Status
This repository follows CASE community guidance on describing [development status](https://caseontology.org/resources/github_policies.html#development-statuses), by adherence to noted support requirements.

The status of this repository is:

4 - Beta

Version notes:
- 0.1.0 - Initial release of Beta

- 0.1.1 - Update to Beta release to deal with removal of rdflib-jsonld (unused import)

    [Show Archived Status of rdflib-jsonld](https://github.com/RDFLib/rdflib-jsonld)

- 0.1.2 - Case 1.2.0 support
	- fixes to some of the vocabulary used in the code for clarity
	- new flag for deterministic uuids in certain instances
	- thanks to @ajnelson-nist for all the PRs on this one

- 0.2.0 - Case 1.3.0 support
	- testing in Python 3.12
