#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import xlsxwriter

import constantes as cte
import data2excel as excel

"""
Constantes locales
"""

qc = "../{}".format(cte.qcaln)
cov = "../{}".format(cte.covarx)
covGens = "../{}".format(cte.covstats)
stats = cte.variantstats
rawData = "raw.reanno.tsv"
maxMaf = 0.01
vafBaja = 2.0
minReads = 10

# Orden de las columnas en que se colocaran en cada una de las pestanas del excel. Estos son los nombres de las columnas en los archivos .reanno.tsv
orden = ["sample", "Gene.refGene", "Chr", "Start", "End", "Ref", "Alt", "GT", "GQ", "MQ", "Func.refGene", "ExonicFunc.refGene", "AAChange.refGene", "GeneDetail.refGene",
"Ref_depth", "Alt_depth", "DP", "AD", "ADF", "ADR", "VAF", "FILTER", "population_max", "population_max_name", "gnomad_exome_AF_popmax", "gnomad_exome_non_topmed_AF_popmax",
"gnomad_genome_AF_popmax", "gnomad_genome_non_topmed_AF_popmax",
"predictor_summary", "Strand_bias_score", "SB",
"avsnp150", "CLNALLELEID", "CLNDN", "CLNDISDB", "CLNREVSTAT", "CLNSIG", "cosmic70",
"SIFT_score", "SIFT_pred", "Polyphen2_HDIV_score", "Polyphen2_HDIV_pred", "Polyphen2_HVAR_score", "Polyphen2_HVAR_pred",
"LRT_score", "LRT_pred", "MutationTaster_score", "MutationTaster_pred", "MutationAssessor_score", "MutationAssessor_pred", "FATHMM_score", "FATHMM_pred", "PROVEAN_score", "PROVEAN_pred",
"VEST3_score", "MetaSVM_score", "MetaSVM_pred", "MetaLR_score", "MetaLR_pred", "M-CAP_score", "M-CAP_pred", "REVEL_score", "MutPred_score", "CADD_raw", "CADD_phred", "DANN_score",
"fathmm-MKL_coding_score", "fathmm-MKL_coding_pred", "Eigen_coding_or_noncoding", "Eigen-raw", "Eigen-PC-raw", "GenoCanyon_score", "integrated_fitCons_score", "integrated_confidence_value",
"GTEx_V6p_tissue", "GERP++_RS", "phyloP100way_vertebrate", "phyloP20way_mammalian", "phastCons100way_vertebrate", "phastCons20way_mammalian", "SiPhy_29way_logOdds", "Interpro_domain", "GTEx_V6p_gene"]

def crearCabecera(hoja, libro) :
    """Escribir la cabecera del excel en las pestanas de variantes

    Escribe los nombres que tendra cada una de las columnas del excel.

    Parameters
    ----------
        hoja : xlsxwriter.worksheet
            Hoja excel en la que se quiere escribir la cabecera
        libro : xlsxwriter.workbook
            Libro excel para guardar el estilo de la cabecera

    Returns
    -------
        int
            Numero de fila en la que finaliza la cabecera
    """
    titulo = libro.add_format({'bold' : True,
        'align' : 'center',
        'border' : 1,
        'bg_color' :  '#B3E6FF',
        'font_size' : 13
    })

    cabecera = ["Sample", "Analysis", "Interpretation", "Gene", "Chromosome", "Start", "End", "Ref", "Alt", "Genotype", "Genome Quality", "Mapping Quality", "Mutation type",
    "Exonic mutation type", "Amino acid change", "Transcript",
    "Reference depth", "Alterated depth", "Position depth", "Allelic depths", "Forward allelic depths", "Reverse allelic depths", "VAF", "Variant caller filter", "Population max MAF",
    "Population reported max MAF", "gNOMAD Exome popmax", "gNOMAD Exome nonTOPMed popmax", "gNOMAD Genome popmax", "gNOMAD Genome nonTOPMed popmax",
    "Predictor summary", "SMD strand bias score", "Variant caller strand bias score",
    "DBSNP", "ClinVar CLNALLELEID", "ClinVar CLNDN", "ClinVar CLNDISDB", "ClinVar CLNREVSTAT", "Clinvar CLNSIG", "COSMIC",
    "SIFT score", "SIFT pred", "Polyphen2 HDIV score", "Polyphen2 HDIV pred", "Polyphen2 HVAR score", "Polyphen2 HVAR pred",
    "LRT score", "LRT pred", "MutationTaster score", "MutationTaster pred", "MutationAssessor score", "MutationAssessor pred", "FATHMM score", "FATHMM pred", "PROVEAN score", "PROVEAN pred",
    "VEST3 score", "MetaSVM score", "MetaSVM pred", "MetaLR score", "MetaLR pred", "M-CAP score", "M-CAP pred", "REVEL score", "MutPred score", "CADD raw", "CADD phred", "DANN score",
    "fathmm-MKL coding score", "fathmm-MKL coding pred", "Eigen coding or noncoding", "Eigen-raw", "Eigen-PC-raw", "GenoCanyon score", "integrated fitCons score", "integrated confidence value",
    "GTEx V6p tissue", "GERP++ RS", "phyloP100way vertebrate", "phyloP20way mammalian", "phastCons100way vertebrate", "phastCons20way mammalian", "SiPhy 29way logOdds", "Interpro domain", "GTEx V6p gene"]

    cols = 0
    nextLine = 0 # Filas donde se esta escribiendo la cabecera. Se devuelve a la funcion principal para no sobreescribir
    for n in cabecera :
        hoja.write(nextLine, cols, n, titulo)
        cols += 1
    nextLine += 1

    return nextLine

def escribirVariantes(hoja, libro, cnt, empiezaEn) :
    """Escribir los datos de un diccionario en una pestana excel

    Escribe los datos del diccionario pasado por parametro en la pestana pasada por parametro. Se asume que son datos de variantes.

    Parameters
    ----------
        hoja : xlsxwriter.worksheet
            Hoja excel donde se van a guardar los datos
        libro : xlsxwriter.workbook
            Libro excel donde se estan guardando los datos. Se usa para guardar los estilos de la hoja
        cnt : dict
            Diccionario con las variantes que se va a guardar en el excel
        empiezaEn : int
            Fila a partir de la que se empezara a escribir los datos del diccionario

    Returns
    -------
        int
            Numero de fila en la finaliza la escritura el contenido del diccionario
    """
    # Estilos para los predictores
    rojo = libro.add_format({"bg_color" : "#FF4D4D"})
    verde = libro.add_format({"bg_color" : "#43F906"})
    amarillo = libro.add_format({"bg_color" : "#FFFF00"})
    naranja = libro.add_format({"bg_color" : "#FF8000"})
    predictors = ["SIFT_pred", "Polyphen2_HDIV_pred", "Polyphen2_HVAR_pred", "LRT_pred", "MutationTaster_pred", "MutationAssessor_pred", "FATHMM_pred", "PROVEAN_pred", "MetaSVM_pred", "MetaLR_pred"]
    fila = empiezaEn
    columna = 0
    for dic in cnt :
        columna = 0
        for o in orden :
            if columna == 1 :
                columna = 3
            if o in predictors :
                if dic[o] == 'D' : #Todos los predictores anotan una D como deleterea
                    hoja.write(fila, columna, dic[o], rojo)
                elif dic[o] == 'T' : #SIFT, Provean, MetaSVM, MetaLR y FATHMM anotan una T como tolerado
                    hoja.write(fila, columna, dic[o], verde)
                elif dic[o] == 'N' : #LRT, MutationTaster y MutationAssessor anotan una N como tolerado
                    hoja.write(fila, columna, dic[o], verde)
                elif (o == "Polyphen2_HDIV_pred" or o == "Polyphen2_HVAR_pred") and dic[o] == 'P' :
                    hoja.write(fila, columna, dic[o], naranja)
                elif (o == "Polyphen2_HDIV_pred" or o == "Polyphen2_HVAR_pred") and dic[o] == 'B' :
                    hoja.write(fila, columna, dic[o], verde)
                elif o == "MutationTaster_pred" and dic[o] == 'A' :
                    hoja.write(fila, columna, dic[o], rojo)
                elif o == "MutationTaster_pred" and dic[o] == 'P' :
                    hoja.write(fila, columna, dic[o], verde)
                elif o == "MutationAssessor_pred" and dic[o] == 'H' :
                    hoja.write(fila, columna, dic[o], rojo)
                elif o == "MutationAssessor_pred" and dic[o] == 'M' :
                    hoja.write(fila, columna, dic[o], naranja)
                elif o == "MutationAssessor_pred" and dic[o] == 'L' :
                    hoja.write(fila, columna, dic[o], verde)
                else :
                    hoja.write(fila, columna, dic[o])
            elif o == "Chr" and not dic[o].startswith("chr") :
                hoja.write(fila, columna, "chr{}".format(dic[o]))
            elif o == "population_max" :
                try :
                    if float(dic[o]) >= maxMaf :
                        hoja.write(fila, columna, dic[o], rojo)
                    else :
                        hoja.write(fila, columna, dic[o])
                except ValueError :
                    hoja.write(fila, columna, dic[o])
            elif o == "Alt_depth" :
                try :
                    if int(dic[o]) < minReads :
                        hoja.write(fila, columna, dic[o], naranja)
                    else :
                        hoja.write(fila, columna, dic[o])
                except ValueError :
                    hoja.write(fila, columna, dic[o])
            else :
                hoja.write(fila, columna, dic[o])
            columna += 1
        fila += 1
    return fila

def filtrarVariantes() :
    cabecera = True
    alldata = [] # Todas las variantes
    conseq = [] # Variantes exonicas (no sinonimas) o de splicing
    maf = [] # Variantes con MAF mayor de 0.01
    vaf = [] # Variantes con VAF < 2
    cand = [] # Variantes candidates (VAF >= 2 y MAF < 0.01)
    isconseq = False # Flag para guardar la variante en las listas maf, vaf i cand
    with open(rawData, "r") as fi :
        for l in fi :
            isconseq = False
            if cabecera :
                claves = l.strip().split("\t")
                cabecera = False
            else :
                aux = l.strip().split("\t")
                it = 0
                temp = {}
                for c in claves :
                    temp[c] = aux[it]
                    it += 1
                alldata.append(temp)
                # Filtrar variantes codificantes
                if temp["Func.refGene"] == "splicing" :
                    conseq.append(temp)
                    isconseq = True
                elif temp["Func.refGene"] == "exonic" and temp["ExonicFunc.refGene"] != "synonymous SNV" :
                    conseq.append(temp)
                    isconseq = True

                if isconseq : # Filtrar las variantes codificantes por MAF y VAF
                    if temp["population_max"] != "NA" and float(temp["population_max"]) >= maxMaf :
                        maf.append(temp)
                    else :
                        if float(temp["VAF"]) >= vafBaja :
                            cand.append(temp)
                        else :
                            vaf.append(temp)

    return alldata, conseq, maf, vaf, cand

def main(excelName) :
    # Leer el archivo crudo de variantes
    raw, conseq, maf, vaf, cand = filtrarVariantes()
    # Crear el archivo excel
    wb = xlsxwriter.Workbook("{}_VH.xlsx".format(excelName), {"strings_to_numbers" : True})
    # Guardar una hoja vacia para colocar las variantes que pasan el filtro visual
    full = wb.add_worksheet("Filtered_def")
    crearCabecera(full, wb)
    full.freeze_panes(1,0)
    # Guardar la hoja de variantes candidatas. En este caso variantes con VAF >= 2
    full = wb.add_worksheet("VAF>=2%")
    full.activate()
    filaActual = crearCabecera(full, wb)
    filaActual = escribirVariantes(full, wb, cand, filaActual)
    excel.ayudaPredictores(full, wb, filaActual+2)
    # Guardar la hoja de variantes con una VAF baja (< 2)
    full = wb.add_worksheet("VAF<2%")
    filaActual = crearCabecera(full, wb)
    filaActual = escribirVariantes(full, wb, vaf, filaActual)
    excel.ayudaPredictores(full, wb, filaActual+2)
    # Guardar la hoja de las variantes con MAF alta
    full = wb.add_worksheet("HighMAF")
    filaActual = crearCabecera(full, wb)
    filaActual = escribirVariantes(full, wb, maf, filaActual)
    excel.ayudaPredictores(full, wb, filaActual+2)
    # Guardar la hoja de las variantes codificantes y de splicing
    full = wb.add_worksheet("Conseq")
    filaActual = crearCabecera(full, wb)
    filaActual = escribirVariantes(full, wb, conseq, filaActual)
    excel.ayudaPredictores(full, wb, filaActual+2)
    # Guardar la hoja con todas las variantes llamadas
    full = wb.add_worksheet("Raw")
    filaActual = crearCabecera(full, wb)
    filaActual = escribirVariantes(full, wb, raw, filaActual)
    excel.ayudaPredictores(full, wb, filaActual+2)
    # Guardar la hoja con las estadisticas de la muestra
    full = wb.add_worksheet("QC_stats")
    excel.escribirEstadisticas(full, wb)
    print("INFO: Creado archivo excel, con nombre {}, con el resumen de resultados".format("{}_VH.xlsx".format(excelName)))
    wb.close()

if __name__ == "__main__" :
    # Comprobar que todos los archivos necesarios estan creados
    continuar = True
    if not os.path.isfile(qc) :
        print("WARNING: No encontrado el archivo con el control de calidad del alineamiento. Deberia estar en: {}".format(qc))
        continuar = False

    if not os.path.isfile(stats) :
        print("WARNING: No encontrado el archivo con las estadisticas de variantes. Buscado como: {}".format(stats))
        continuar = False

    if not os.path.isfile(cov) :
        print("WARNING: No encontrado el archivo con las estatidisticas de coverage. Buscado como: {}".format(cov))
        continuar = False

    if not os.path.isfile(rawData) :
        print("WARNING: No encontrado el filtro de variantes {}".format(rawData))
        continuar = False

    if continuar :
        if (len(sys.argv) > 1) :
            main(sys.argv[1])
        else :
            main("noName")
    else :
        print("ERROR: No se ha encontrado ninguno de los archivos necesarios. No se puede crear el excel")
        sys.exit(1)
