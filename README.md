<p align="center">
  <img src="static/images/job_logo.png" alt="JOB Logo" width="306" height="200">
</p>

# Japan Omics Browser (JOB)

## Description

The Japan Omics Browser (JOB) is an integrated web application for visualizing and analyzing integrative omics data. JOB offers visualization of per-variant regulatory effects in the human blood at mRNA and protein level distinctively, quantified from statistical fine-mapping of mRNA-expression quantitative loci (eQTL) and protein QTLs (pQTLs) in 1,405 Japanese, together with fine-mapping results of 94 complex traits in UK Biobank. In addition, JOB shows per-tissue regulatory effect prediction score (EMS), trained via multi-task learning. Furthermore, validation scores from  Massively Parallel Reporter Assay (MPRA) in two cell types are available for over 10,000 variants. The application is hosted on the Google Cloud Platform.

### Usage
To use JOB, simply visit : https://japan-omics.jp/

Enter keywords on the search page to navigate to specific pages.

### Dependencies
- Google App Engine
- Google Cloud SQL
- Python(3.8)
- Bootstrap5
- JQuery
- Flask(2.2.3)
- Bokeh(3.1.0)

### Available omics features

- (Marginal) effect sizes, standard error of the effect sizes, posterior inclusion probability (PIP) from statistical fine-mapping of mRNA expression quantitative loci (eQTL) effect in two tools (SuSiE and FINEMAP)
- The same features for protein expression quantitative loci (pQTL)
- PIPs from statistical fine-mapping of UK Biobank phenotype in SuSiE
- Machine learning-based prediction of gene regulatory effect variants for 49 GTEx tissues
- The allelic effect (log2 fold change) measured by the massively parallel reporter assay (MPRA)
