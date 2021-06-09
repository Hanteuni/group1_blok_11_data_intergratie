Data intergratie groep 1 pipeline
------
#### Pipeline van het data intergratie project
![pipeline data intergratie](https://github.com/Hanteuni/group1_blok_11_data_intergratie/blob/main/pipline_data_intergration.png)


Requirements*:
---
```
Linux LTS 
Nextflow
SnpEFF deze kan gedownload worden van [hier](https://pcingola.github.io/SnpEff/download/). De SNPEff folder die gedownload is dient geplaatst te worden in dezelfde folder als waar pipeline.nf in komt te staan.

*Let op dat zowel de vcf als pdf bestanden in de input folder komen te staan.
```

### Running the pipeline
To run the pipeline simply use the following command
** Let op; Deze github is al voorzien van 1 PDF sample (PCGP 1) en geen VCF samples.  **
```
bash nextflow pipeline.nf
```



