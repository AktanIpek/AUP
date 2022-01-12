#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MAIN: Libreria con funciones para re-anotar y filtrar un archivo de salida de table_annovar. Esta libreria se usa para scripts, como filtMutect o filtStrelka para extraer datos en comun
"""
import sys
import getWebInfo as gw

# Constantes
vafBaja = 2 # VAF para considerar una variante como candidata o de baja VAF. Modificar la documentacion de la funcion filtrarVAF en caso de modificar esta constante
minMaf = 0.01 # MAF para considerar una variante como poblacional o posible candidata. Modificar la documentacion de la funcion filtrarMAF en caso de modificar esta constante

#Todas las claves con la informacion que se guardara en los archivos de texto
allkeys = ["Chr", "Start", "End", "Ref", "Alt", "Func.refGene", "Gene.refGene", "GeneDetail.refGene", "ExonicFunc.refGene", "AAChange.refGene", "avsnp150", "1000g2015aug_all",
"1000g2015aug_afr", "1000g2015aug_amr", "1000g2015aug_eas", "1000g2015aug_eur", "1000g2015aug_sas", "ExAC_ALL", "ExAC_AFR", "ExAC_AMR", "ExAC_EAS", "ExAC_FIN", "ExAC_NFE", "ExAC_OTH",
"ExAC_SAS", "gnomad_exome_AF", "gnomad_exome_AF_popmax", "gnomad_exome_AF_male", "gnomad_exome_AF_female", "gnomad_exome_AF_raw", "gnomad_exome_AF_afr", "gnomad_exome_AF_sas",
"gnomad_exome_AF_amr", "gnomad_exome_AF_eas", "gnomad_exome_AF_nfe", "gnomad_exome_AF_fin", "gnomad_exome_AF_asj", "gnomad_exome_AF_oth", "gnomad_exome_non_topmed_AF_popmax",
"gnomad_exome_non_neuro_AF_popmax", "gnomad_exome_non_cancer_AF_popmax", "gnomad_exome_controls_AF_popmax", "gnomad_genome_AF", "gnomad_genome_AF_popmax", "gnomad_genome_AF_male",
"gnomad_genome_AF_female", "gnomad_genome_AF_raw", "gnomad_genome_AF_afr", "gnomad_genome_AF_sas", "gnomad_genome_AF_amr", "gnomad_genome_AF_eas", "gnomad_genome_AF_nfe",
"gnomad_genome_AF_fin", "gnomad_genome_AF_asj", "gnomad_genome_AF_oth", "gnomad_genome_non_topmed_AF_popmax", "gnomad_genome_non_neuro_AF_popmax", "gnomad_genome_non_cancer_AF_popmax",
"gnomad_genome_controls_AF_popmax", "esp6500siv2_all", "esp6500siv2_ea", "esp6500siv2_aa", "CLNALLELEID", "CLNDN", "CLNDISDB", "CLNREVSTAT", "CLNSIG", "cosmic70", "SIFT_score",
"SIFT_converted_rankscore", "SIFT_pred", "Polyphen2_HDIV_score", "Polyphen2_HDIV_rankscore", "Polyphen2_HDIV_pred", "Polyphen2_HVAR_score", "Polyphen2_HVAR_rankscore", "Polyphen2_HVAR_pred",
"LRT_score", "LRT_converted_rankscore", "LRT_pred", "MutationTaster_score", "MutationTaster_converted_rankscore", "MutationTaster_pred", "MutationAssessor_score",
"MutationAssessor_score_rankscore", "MutationAssessor_pred", "FATHMM_score", "FATHMM_converted_rankscore", "FATHMM_pred", "PROVEAN_score", "PROVEAN_converted_rankscore", "PROVEAN_pred",
"VEST3_score", "VEST3_rankscore", "MetaSVM_score", "MetaSVM_rankscore", "MetaSVM_pred", "MetaLR_score", "MetaLR_rankscore", "MetaLR_pred", "M-CAP_score", "M-CAP_rankscore", "M-CAP_pred",
"REVEL_score", "REVEL_rankscore", "MutPred_score", "MutPred_rankscore", "CADD_raw", "CADD_raw_rankscore", "CADD_phred", "DANN_score", "DANN_rankscore", "fathmm-MKL_coding_score",
"fathmm-MKL_coding_rankscore", "fathmm-MKL_coding_pred", "Eigen_coding_or_noncoding", "Eigen-raw", "Eigen-PC-raw", "GenoCanyon_score", "GenoCanyon_score_rankscore", "integrated_fitCons_score",
"integrated_fitCons_score_rankscore", "integrated_confidence_value", "GERP++_RS", "GERP++_RS_rankscore", "phyloP100way_vertebrate", "phyloP100way_vertebrate_rankscore",
"phyloP20way_mammalian", "phyloP20way_mammalian_rankscore", "phastCons100way_vertebrate", "phastCons100way_vertebrate_rankscore",  "phastCons20way_mammalian",
"phastCons20way_mammalian_rankscore", "SiPhy_29way_logOdds", "SiPhy_29way_logOdds_rankscore", "Interpro_domain", "GTEx_V6p_gene", "GTEx_V6p_tissue", "CHROM", "POS", "ID", "REFERENCE",
"ALTERATED", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLE", "END", "BLOCKAVG", "SNVHPOL", "CIGAR", "RU", "REFPREP", "IDREP", "MQ", "GT", "GQ", "GQX", "DP", "DPF", "MIN_DP", "AD",
"ADF", "ADR", "FT", "DPI", "PL", "PS", "SB", "population_max", "population_max_name", "predictor_summary", "Strand_bias_score", "Ref_depth", "Alt_depth", "VAF", "IGV_link", "sample","CADD_1000g_all",
"CADD_1000g_afr", "CADD_1000g_amr", "CADD_1000g_eur", "CADD_1000g_eas", "CADD_1000g_sas", "dbNSFP_1000g_all", "dbNSFP_1000g_afr", "dbNSFP_1000g_amr", "dbNSFP_1000g_eur", "dbNSFP_1000g_eas",
"dbNSFP_1000g_sas", "CADD_ESP6500_all", "CADD_ESP6500_ea", "CADD_ESP6500_aa","dbNSFP_esp6500_all", "dbNSFP_esp6500_ea", "dbNSFP_esp6500_aa", "ExAC_ExAC_all", "ExAC_ExAC_afr","ExAC_ExAC_amr",
"ExAC_ExAC_eas", "ExAC_ExAC_fin", "ExAC_ExAC_nfe", "ExAC_ExAC_oth", "ExAC_ExAC_sas", "dbNSFP_ExAC_all", "dbNSFP_ExAC_afr", "dbNSFP_ExAC_amr", "dbNSFP_ExAC_eas", "dbNSFP_ExAC_fin",
"dbNSFP_ExAC_nfe", "dbNSFP_ExAC_oth", "dbNSFP_ExAC_sas", "gNOMAD_Exome_all", "gNOMAD_Exome_afr", "gNOMAD_Exome_amr", "gNOMAD_Exome_asj", "gNOMAD_Exome_eas", "gNOMAD_Exome_fin",
"gNOMAD_Exome_nfe", "gNOMAD_Exome_oth", "gNOMAD_Exome_popmax", "gNOMAD_Exome_raw", "gNOMAD_Exome_sas", "gNOMAD_Genome_all", "gNOMAD_Genome_afr", "gNOMAD_Genome_amr", "gNOMAD_Genome_asj",
"gNOMAD_Genome_eas", "gNOMAD_Genome_fin", "gNOMAD_Genome_nfe", "gNOMAD_Genome_oth", "gNOMAD_Genome_popmax", "gNOMAD_Genome_raw", "dbSNP_MAF"]

# Cuando un dato no este disponible se guarda el siguinte caracter
vacio = "--"

#Columnas que contienen informacion de MAF
mafCols = ["1000g2015aug_all", "1000g2015aug_afr", "1000g2015aug_amr", "1000g2015aug_eas", "1000g2015aug_eur", "1000g2015aug_sas", "ExAC_ALL", "ExAC_AFR", "ExAC_AMR", "ExAC_EAS", "ExAC_FIN",
"ExAC_NFE", "ExAC_OTH", "ExAC_SAS", "gnomad_exome_AF", "gnomad_exome_AF_popmax", "gnomad_exome_AF_male", "gnomad_exome_AF_female", "gnomad_exome_AF_raw", "gnomad_exome_AF_afr",
"gnomad_exome_AF_sas", "gnomad_exome_AF_amr", "gnomad_exome_AF_eas", "gnomad_exome_AF_nfe", "gnomad_exome_AF_fin", "gnomad_exome_AF_asj", "gnomad_exome_AF_oth", "gnomad_exome_non_topmed_AF_popmax",
"gnomad_exome_non_neuro_AF_popmax", "gnomad_exome_non_cancer_AF_popmax", "gnomad_exome_controls_AF_popmax", "gnomad_genome_AF", "gnomad_genome_AF_popmax", "gnomad_genome_AF_male",
"gnomad_genome_AF_female", "gnomad_genome_AF_raw", "gnomad_genome_AF_afr", "gnomad_genome_AF_sas", "gnomad_genome_AF_amr", "gnomad_genome_AF_eas", "gnomad_genome_AF_nfe",
"gnomad_genome_AF_fin", "gnomad_genome_AF_asj", "gnomad_genome_AF_oth", "gnomad_genome_non_topmed_AF_popmax", "gnomad_genome_non_neuro_AF_popmax", "gnomad_genome_non_cancer_AF_popmax",
"gnomad_genome_controls_AF_popmax", "esp6500siv2_all", "esp6500siv2_ea", "esp6500siv2_aa", "CADD_1000g_all", "CADD_1000g_afr", "CADD_1000g_amr", "CADD_1000g_eur", "CADD_1000g_eas",
"CADD_1000g_sas", "dbNSFP_1000g_all", "dbNSFP_1000g_afr", "dbNSFP_1000g_amr", "dbNSFP_1000g_eur", "dbNSFP_1000g_eas", "dbNSFP_1000g_sas", "CADD_ESP6500_all", "CADD_ESP6500_ea", "CADD_ESP6500_aa",
"dbNSFP_esp6500_all", "dbNSFP_esp6500_ea", "dbNSFP_esp6500_aa", "ExAC_ExAC_all", "ExAC_ExAC_afr","ExAC_ExAC_amr", "ExAC_ExAC_eas", "ExAC_ExAC_fin", "ExAC_ExAC_nfe", "ExAC_ExAC_oth",
"ExAC_ExAC_sas", "dbNSFP_ExAC_all", "dbNSFP_ExAC_afr", "dbNSFP_ExAC_amr", "dbNSFP_ExAC_eas", "dbNSFP_ExAC_fin", "dbNSFP_ExAC_nfe", "dbNSFP_ExAC_oth", "dbNSFP_ExAC_sas", "gNOMAD_Exome_all",
"gNOMAD_Exome_afr", "gNOMAD_Exome_amr", "gNOMAD_Exome_asj", "gNOMAD_Exome_eas", "gNOMAD_Exome_fin", "gNOMAD_Exome_nfe", "gNOMAD_Exome_oth", "gNOMAD_Exome_popmax", "gNOMAD_Exome_raw",
"gNOMAD_Exome_sas", "gNOMAD_Genome_all", "gNOMAD_Genome_afr", "gNOMAD_Genome_amr", "gNOMAD_Genome_asj", "gNOMAD_Genome_eas", "gNOMAD_Genome_fin", "gNOMAD_Genome_nfe", "gNOMAD_Genome_oth",
"gNOMAD_Genome_popmax", "gNOMAD_Genome_raw", "dbSNP_MAF"]

def addFORMAT(dic) :
    """Separar los datos de las columnas INFO y FORMAT del vcf en columnas

    Separar los datos de las columnas INFO y FORMAT del vcf en columnas. Se devuelven los datos separados en un diccionario. Se comprueba si alguna clave esta ya presente en el diccionario
    para no sobreescribir los datos de dicha columna.

    Parameters
    ----------
        dic : dict
            Linea del table_annovar (variante) de la que extraer la informacion. Se asume que el diccionario tendra las claves FORMAT e INFO

    Returns
    -------
        dict
            Diccionario con los datos de FORMAT e INFO separados
    """
    claves = dic["FORMAT"].split(":")
    valores = dic["SAMPLE"].split(":")
    minidic = {}
    i = 0
    #Separar los datos de la columna FORMAT en distintas columnas
    for c in claves :
        if c in dic.keys() :
            print("WARNING: Clave {} repetida en {}".format(c, dic.keys()))
            sys.exit()
        else :
            minidic[c] = valores[i]
        i += 1

    #Separar los datos de la columna INFO en distintas columnas
    datos = dic["INFO"].split(";")
    for d in datos :
        aux = d.split("=")
        aux[0] = "{}_INFO".format(aux[0])
        if aux[0] in dic.keys() or aux[0] in minidic.keys():
            print("WARNING: Clave {} repetida al montar INFO".format(aux[0]))
            sys.exit()
        if len(aux) == 1 :
            minidic[aux[0]] = aux[0]
        else :
            minidic[aux[0]] = aux[1]
    return minidic

def convertirData(path) :
    """Abrir un archivo con formato table_annovar y guardar todo el contenido en un diccionario

    Convierte un vcf, anotado por ANNOVAR, en un diccionario. Separa los datos de la columna FORMAT y la columna INFO, y los agrega al diccionario, usando la funcion addFORMAT

    Parameters
    ----------
        path : str
            Ruta del archivo a convertir en diccionario

    Returns
    -------
        dict
            Contenido del archivo ANNOVAR en formato diccionario de Python
    """
    cabecera = True
    temp = {}
    # Columnas dentro del table_annovar
    claves = ["Chr", "Start", "End", "Ref", "Alt", "Func.refGene", "Gene.refGene", "GeneDetail.refGene", "ExonicFunc.refGene", "AAChange.refGene", "avsnp150", "1000g2015aug_all",
    "1000g2015aug_afr", "1000g2015aug_amr", "1000g2015aug_eas", "1000g2015aug_eur", "1000g2015aug_sas", "ExAC_ALL", "ExAC_AFR", "ExAC_AMR", "ExAC_EAS", "ExAC_FIN", "ExAC_NFE", "ExAC_OTH",
    "ExAC_SAS", "gnomad_exome_AF", "gnomad_exome_AF_popmax", "gnomad_exome_AF_male", "gnomad_exome_AF_female", "gnomad_exome_AF_raw", "gnomad_exome_AF_afr", "gnomad_exome_AF_sas",
    "gnomad_exome_AF_amr", "gnomad_exome_AF_eas", "gnomad_exome_AF_nfe", "gnomad_exome_AF_fin", "gnomad_exome_AF_asj", "gnomad_exome_AF_oth", "gnomad_exome_non_topmed_AF_popmax",
    "gnomad_exome_non_neuro_AF_popmax", "gnomad_exome_non_cancer_AF_popmax", "gnomad_exome_controls_AF_popmax", "gnomad_genome_AF", "gnomad_genome_AF_popmax", "gnomad_genome_AF_male",
    "gnomad_genome_AF_female", "gnomad_genome_AF_raw", "gnomad_genome_AF_afr", "gnomad_genome_AF_sas", "gnomad_genome_AF_amr", "gnomad_genome_AF_eas", "gnomad_genome_AF_nfe",
    "gnomad_genome_AF_fin", "gnomad_genome_AF_asj", "gnomad_genome_AF_oth", "gnomad_genome_non_topmed_AF_popmax", "gnomad_genome_non_neuro_AF_popmax", "gnomad_genome_non_cancer_AF_popmax",
    "gnomad_genome_controls_AF_popmax", "esp6500siv2_all", "esp6500siv2_ea", "esp6500siv2_aa", "CLNALLELEID", "CLNDN", "CLNDISDB", "CLNREVSTAT", "CLNSIG", "cosmic70", "SIFT_score",
    "SIFT_converted_rankscore", "SIFT_pred", "Polyphen2_HDIV_score", "Polyphen2_HDIV_rankscore", "Polyphen2_HDIV_pred", "Polyphen2_HVAR_score", "Polyphen2_HVAR_rankscore", "Polyphen2_HVAR_pred",
    "LRT_score", "LRT_converted_rankscore", "LRT_pred", "MutationTaster_score", "MutationTaster_converted_rankscore", "MutationTaster_pred", "MutationAssessor_score",
    "MutationAssessor_score_rankscore", "MutationAssessor_pred", "FATHMM_score", "FATHMM_converted_rankscore", "FATHMM_pred", "PROVEAN_score", "PROVEAN_converted_rankscore", "PROVEAN_pred",
    "VEST3_score", "VEST3_rankscore", "MetaSVM_score", "MetaSVM_rankscore", "MetaSVM_pred", "MetaLR_score", "MetaLR_rankscore", "MetaLR_pred", "M-CAP_score", "M-CAP_rankscore", "M-CAP_pred",
    "REVEL_score", "REVEL_rankscore", "MutPred_score", "MutPred_rankscore", "CADD_raw", "CADD_raw_rankscore", "CADD_phred", "DANN_score", "DANN_rankscore", "fathmm-MKL_coding_score",
    "fathmm-MKL_coding_rankscore", "fathmm-MKL_coding_pred", "Eigen_coding_or_noncoding", "Eigen-raw", "Eigen-PC-raw", "GenoCanyon_score", "GenoCanyon_score_rankscore", "integrated_fitCons_score",
    "integrated_fitCons_score_rankscore", "integrated_confidence_value", "GERP++_RS", "GERP++_RS_rankscore", "phyloP100way_vertebrate", "phyloP100way_vertebrate_rankscore",
    "phyloP20way_mammalian", "phyloP20way_mammalian_rankscore", "phastCons100way_vertebrate", "phastCons100way_vertebrate_rankscore",  "phastCons20way_mammalian",
    "phastCons20way_mammalian_rankscore", "SiPhy_29way_logOdds", "SiPhy_29way_logOdds_rankscore", "Interpro_domain", "GTEx_V6p_gene", "GTEx_V6p_tissue", "CHROM", "POS", "ID", "REFERENCE",
    "ALTERATED", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLE"]
    with open(path, "r") as fi :
        dc = []
        for l in fi :
            if cabecera :
                cabecera = False
            else :
                aux = l.strip().split("\t")
                i = 0
                for c in claves :
                    temp[c] = aux[i]
                    i += 1
                aux2 = addFORMAT(temp)
                temp.update(aux2)
                dc.append(temp)
                temp = {}
    return dc

def filtroPAS(dc) :
    """Seleccionar solo las variantes que tengan como filtro PASS segun Strelka2

    Dado una lista de diccionarios (tabla de variantes) pasada por parametro, crea una nueva lista con aquellas variantes que han pasado los filtros del variant caller Strelka2

    Parameters
    ----------
        dc : list
            Lista de diccionarios con el contenido que se quiere filtrar

    Returns
    -------
        list
            Lista de diccionarios con aquellas variantes que han pasado este filtro
    """
    nuevo = []
    for d in dc :
        if d["FILTER"] == "PASS" :
            nuevo.append(d)
    return nuevo

def filtroConseq(dc) :
    """Selecciona aquellas variantes que son exonicas (excluye sinonimas) y splicing

    Dada una lista de diccionarios (lista de variantes) pasada por parametro, crea una nueva lista con aquellas variantes que se encuentren en zonas codificantes (exonic) que no sean
    sinonimas, o variantes en regiones de splicing.

    Parameters
    ----------
        dc : list
            Lista de diccionarios con el contenido a filtrar

    Returns
    -------
        list
            Lista de diccionarios con aquellas variantes que han pasado este filtro
    """
    nuevo = []
    for d in dc :
        if d["Func.refGene"] == "splicing" :
            nuevo.append(d)
        elif d["Func.refGene"] == "exonic" and d["ExonicFunc.refGene"] != "synonymous SNV" :
            nuevo.append(d)
    return nuevo

def filtrarMAF(dc) :
    """Clasificar las variantes por su Minor Allele Frequency

    Dada una lista de diccionarios (variantes), separar las variantes respecto a la MAF. Considera MAF alta aquellas variantes con, almenos, una columna de poblacion con valor mayor
    o igual a 0.01 (1%). El resto se consideran con MAF baja

    Parameters
    ----------
        dc : list
            Lista de diccionarios con el contenido a separar

    Returns
    -------
        alta : list
            Variantes con MAF mayor o igual que el umbral
        baja : list
            Variantes con MAF menor que el umbral
    """
    baja = []
    alta = []
    for l in dc :
        if l["population_max"] != "NA" and l["population_max"] >= minMaf :
            alta.append(l)
        else :
            baja.append(l)
    return alta, baja

def filtrarVAF(dc) :
    """Clasificar las variantes por su Variant Allele Frequency

    Dada una lista de diccionarios (variantes) pasada por parametro, separa los elementos de la lista dependiendo de la frecuencia alelica de la variante (VAF). Se consideran variantes
    con una VAF alta aquellas que tengan una VAF mayor de 2(%). Si la VAF es menor o igual al 2% se considera que es baja

    Parameters
    ----------
        dc : list
            Lista de diccionarios con el contenido a separar

    Returns
    -------
        alta : list
            Variantes con VAF mayor que el umbral
        baja : list
            Variantes con VAF menor o igual al umbral
    """
    alta = []
    baja = []
    for l in dc :
        if l["VAF"] >= vafBaja :
            alta.append(l)
        else :
            baja.append(l)
    return alta, baja

def addWebInfo(dc) :
    """Agregar la informacion de myvariant.info a aquellas variantes que sean exonicas

    Usa la funcion getMyVariant, de la libreria getWebInfo para conseguir dichos datos. Una vez conseguidos, agrega la informacion al diccionario pasado por parametro

    Parameters
    ----------
        dc : dict
            Variante de la que se va a buscar la informacion en myvariant.info

    Returns
    -------
        dict
            Mismos datos pasados por parametro, junto con los datos obtenidos de myvariant.info
    """
    for d in dc :
        aux = gw.getMyVariant(d["Chr"], d["Start"], d["Ref"], d["Alt"])
        d.update(aux)
    return dc

def guardarTabla(dc, prefijo) :
    """Guardar las variantes pasadas por parametro en un archivo de texto con formato de tabla.

    Guarda una lista de diccionarios (variantes) en un archivo de con formato tsv. El orden de las columnas viene en la constante allkeys. En caso de no encontrarse la clave dentro del
    diccionario, se guarda el valor de la constante vacio.

    Parameters
    ----------
        dc : list
            Lista de diccionarios. Cada elemento de la lista es un diccionario con los datos de una variante encontrada
        prefijo : str
            Nombre que tendra el archivo. El nombre de archivo se compone de este parametro y la constante sufijo (.reanno.tsv)
    """
    sufijo = "reanno.tsv"
    filename = "{}.{}".format(prefijo, sufijo)
    with open(filename, "w") as fi :
        fi.write("\t".join(allkeys))
        fi.write("\n")
        for d in dc :
            for o in allkeys :
                if o in d.keys() :
                    fi.write("{}\t".format(d[o]))
                else :
                    fi.write("{}\t".format(vacio))
            fi.write("\n")
    print("INFO: Guardado archivo {}".format(filename))

def maximMaf(dc) :
    """Obtener el valor maximo de MAF

    Calcula la maxima MAF (Minor Allele Frequency) de todas las columnas con informacion de este tipo en la variante pasada por parametro. El nombre de las columnas con MAF viene definido
    en la constante mafCols. En caso de no encontrar datos de MAF en las columnas, devuelve NA

    Parameters
    ----------
        dc : dict
            Variante, en formato dict, de la que se quiere obtener el valor de MAF mas alto

    Returns
    -------
        maxim : float, str
            Si se encuentra, almenos, una MAF dentro de las columnas de variantes poblacionales, se devolvera el valor maximo encontrado. En caso de no encontrarse ningun valor de MAF,
            devuelve 'NA'
        poblacio : str
            Nombre de la columna en la que se ha detectado el valor maximo de MAF
    """
    maxim = -1
    poblacio = ""
    for i in mafCols :
        if i in dc.keys() and dc[i] != 'NA' and dc[i] != '.' and float(dc[i]) > maxim:
            maxim = float(dc[i])
            poblacio = i
    if maxim == -1 :
        maxim = 'NA'

    return maxim, poblacio

def resumPredictors(d) :
    """Resumir 11 predictores in silico

    Comprueba los resultados obtenidos en SIFT, Polyphen2 HDIV, Polyphen2 HVAR, LRT, Mutation Taster, Mutation Assessor, FATHMM, Provean, MetaSVM, MetaLR y DANN. Agrupa los resultados obtenidos
    en formato {}D, {}T, {}U donde:
        * D es el numero de predictores que predicen la variante como deleterea
        * T es el numero de predictores que predicen la variante como tolerada
        * U es el numero de predictores que no pueden dar un resultado fiable a la variante (prediccion desconocida, o no significativa)

    Parameters
    ----------
        d : dict
            Variante en la que se quiere averiguar los resultados de los predictores

    Returns
    -------
        str
            Resumen de los predictores. El formato de la cadena es _D, _T, _U donde D es el numero de predicciones deletereas, T el numero de predicciones toleradas y U el numero de
            predicciones desconocidas
    """
    deleterious = 0
    tolerated = 0
    unknown = 0
    if d["SIFT_pred"] == 'D' :
        deleterious += 1
    elif d["SIFT_pred"] == 'T' :
        tolerated += 1
    else :
        unknown += 1
    if d["Polyphen2_HDIV_pred"] == 'D' or d["Polyphen2_HDIV_pred"] == 'P' :
        deleterious += 1
    elif d["Polyphen2_HDIV_pred"] == 'B' :
        tolerated += 1
    else :
        unknown += 1
    if d["Polyphen2_HVAR_pred"] == 'D' or d["Polyphen2_HVAR_pred"] == 'P' :
        deleterious += 1
    elif d["Polyphen2_HVAR_pred"] == 'B' :
        tolerated += 1
    else :
        unknown += 1
    if d["LRT_pred"] == 'D' :
        deleterious += 1
    elif d["LRT_pred"] == 'N' :
        tolerated += 1
    else :
        unknown += 1
    if d["MutationTaster_pred"] == 'A' or d["MutationTaster_pred"] == 'D' :
        deleterious += 1
    elif d["MutationTaster_pred"] == 'N' or d["MutationTaster_pred"] == 'P' :
        tolerated += 1
    else :
        unknown += 1
    if d["MutationAssessor_pred"] == 'H' or d["MutationAssessor_pred"] == 'M' :
        deleterious += 1
    elif d["MutationAssessor_pred"] == 'L' or d["MutationAssessor_pred"] == 'N' :
        tolerated += 1
    else :
        unknown += 1
    if d["FATHMM_pred"] == 'D' :
        deleterious += 1
    elif d["FATHMM_pred"] == 'T' :
        tolerated += 1
    else :
        unknown += 1
    if d["PROVEAN_pred"] == 'D' :
        deleterious += 1
    elif d["PROVEAN_pred"] == 'T' :
        tolerated += 1
    else :
        unknown += 1
    if d["MetaSVM_pred"] == 'D' :
        deleterious += 1
    elif d["MetaSVM_pred"] == 'T' :
        tolerated += 1
    else :
        unknown += 1
    if d["MetaLR_pred"] == 'D' :
        deleterious += 1
    elif d["MetaLR_pred"] == 'T' :
        tolerated += 1
    else :
        unknown += 1

    if d["DANN_score"] == "NA" or d["DANN_score"] == "." :
        unknown += 1
    elif float(d["DANN_score"]) > 0.9 :
        deleterious += 1
    elif float(d["DANN_score"]) <= 0.9 :
        tolerated += 1

    return "{}D, {}T, {}U".format(deleterious, tolerated, unknown)
