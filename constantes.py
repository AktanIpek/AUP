#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    Constantes que se usan en cada una de los scripts de AUP
"""

workindir = "/home/ffuster/panalisi/resultats" # Directorio de trabajo donde se guardan los analisis hechos

# Rutas de los programas que se ejecutan durante el analisis tipico de paneles
fastqc = "/opt/FastQC/fastqc"
bwa = "/opt/bwa.kit/bwa"
picard = "/opt/picard-tools-2.21.8/picard.jar"
bedtools = "bedtools"
gatk = "/opt/gatk-4.1.8.0/gatk"
strelka2 = "/opt/strelka-2.9.10"
samtools = "samtools"
varscan = "/opt/varscan-2.4.0/VarScan.v2.4.0.jar"
annovar = "/opt/annovar20200607"
annovar_db = "/home/ffuster/share/biodata/Indexes/ANNOVAR/humandb/"

# Rutas de los archivos necesarios para el analisis (genomas de referencia, manifest...)
genoma_referencia = "/home/ffuster/share/gsole/genomes_referencia/ucsc/hg19.fa"
dbsnp = "/home/ffuster/share/gsole/genomes_referencia/gnomad.exomes.r2.1.1.sites.vcf.gz" # Descargado desde https://gnomad.broadinstitute.org/downloads. Comprimido usando bgzip (samtools) e indexado usando tabix
# Archivos de manifest. Actualizar ruta en caso de cambiar el manifest
manifest = "/home/ffuster/panalisi/resultats/manifest_Roche/manifest.bed"
gzmanifest = "/home/ffuster/panalisi/resultats/manifest_Roche/manifest.bed.gz"
manifestidx = "/home/ffuster/panalisi/resultats/manifest_Roche/manifest.bed.gz.tbi"
genes = "/home/ffuster/panalisi/resultats/manifest_Roche/gensAestudi.txt"

prefijoTanda = "tanda" # Prefijo que tiene todas las tandas analizadas
scriptdir = "/home/ffuster/AUP" # Directorio de trabajo donde estan los scripts

# Archivos de salida necesarios para entrada. Algunos scripts los usan para calcular algunos datos
bedoutput = "bwa.bed"
finalbam = "bwa.recal.bam"
fastqcdir = "fastqc"

# Archivos de calidad. Se usan para crear una pestaña en el excel final con ellos
qcaln = "alnQC.txt"
covarx = "coverage.txt"
covstats = "coverageGeneStats.tsv" # NOTA: En caso de modificar esta constante, modificar la constante de coveragePanells.R
variantstats = "variants.stats.txt"

# Ruta para encontrar las plantillas para los informes web
pathTemplate = "/home/ffuster/AUP/informes/informe.html"
pathCss = "/home/ffuster/AUP/informes/estils.css"

# Ruta para encontrar las plantillas para los informes web de la tanda entera
pathAllTemplate = "/home/ffuster/AUP/informes/qcGlobal.html"
pathAllCss = "/home/ffuster/AUP/informes/estilosQC.css"
pathAllJs = "/home/ffuster/AUP/informes/funcionesQC.js"
