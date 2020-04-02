#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MAIN: Funciones para crear el log de analisis de los paneles
"""

"""
FUNCTIONS:
    prepararScript - Crea el bash con todos los comandos que se van a usar en el análisis del panel
    extraerRG - Extrae el Read Group de los FASTQ
    FALTEN FUNCIONS PER POSCAR ACI
"""
import os

"""
CONSTANTS:
    Rutas de los programas y parametros de cada uno de los pasos dentro de la pipeline
"""
# IDEA: Podrien ser getters amb els parametres per defecte. Seria mes llegible
fastqc = "/opt/FastQC/fastqc -o fastqc/ -f fastq -extract -q -t 6 {fastq}" #Comando para ejecutar FastQC (control de calidad de los FASTQ). Los parametros indican -o ruta donde se guardaran los archivos de salida. -f que el archivo de entrada es un FASTQ -extract descomprimir el archivo de salida -q omite los mensajes de progreso (log) -t 6 el numero de hilos (threads) que usa el programa para ejcutarse en paralelo
bwa = "/opt/bwa.kit/bwa mem -M -t 6 -R {rg} {ref} {fw} {rv} > bwa.sam" # Comando para ejecutar BWA (alineamiento). Los parametros indican -M para compatibilidad con Picard tools y GATk -t numero de hilos (threads) que usa el programa para ejecutarse -R Read Group que se pondra en el sam de salida. Este Read Group es necesario para poder ejecutar GATK (post-alineamiento)
picardSort = "java -jar /opt/picard-tools-2.21.8/picard.jar SortSam INPUT=bwa.sam OUTPUT=bwa.sort.bam SORT_ORDER=coordinate" # Comando para ordenar el bam
picardIndex = "java -jar /opt/picard-tools-2.21.8/picard.jar BuildBamIndex INPUT={bam}" # Comando para crear un indice en el bam ordenado
bedtoolsBam2Bed = "bedtools bamtobed -i {bam} > bwa.bed" #Comando para crear un bed con todas las regiones donde se han alineado reads
gatk1 = "/opt/gatk-4.1.4.1/gatk BaseRecalibrator -I {bam} -R {ref} --known-sites {dbsnp} -O recaldata.table" # Comando para realizar el primer paso de la recalibracion de bases sugerida por GATK
gatk2 = "/opt/gatk-4.1.4.1/gatk ApplyBQSR -I {bam} -R {ref} -bqsr-recal-file recaldata.table -O bwa.recal.bam" # Comando para realizar el segundo paso de la recalibracion de bases sugerida por GATK
markDup = "java -jar /opt/picard-tools-2.21.8/picard.jar MarkDuplicates INPUT={bam} OUTPUT=bwa.nodup.bam METRICS_FILE=dups_bam.txt" # Comando para marcar duplicados usando Picard tools


vc = "" #Ruta al variant caller que se va a usar (Strelka2)
anno = "" #Ruta al ANNOVAR (anotador de variantes)
cov = "" #Script de coverage que se va a hacer

referencia = "/home/ffuster/panalisi/referencies/gatkHg19.fa"
manifest = "/home/ffuster/panalisi/resultats/manifest.bed"
# Descargado desde https://gnomad.broadinstitute.org/downloads
indels = "/home/ffuster/panalisi/referencies/gold_indels.vcf" # TODO: Arxiu a eliminar
dbsnp = "/home/ffuster/share/biodata/solelab/referencies/gnomad.exomes.r2.1.1.sites.vcf"
genes = "/home/ffuster/panalisi/resultats/gensAestudi.txt"

pathAnalisi = "/home/ffuster/panalisi/resultats" # Ruta donde se ejecutan y guardan los analisis
prefijoTanda = "tanda" # Prefijo que tiene todas las tandas analizadas

def extraerRG(fastq) :
    """
    Extrae el Read Group de un archivo FASTQ.

    Se espera el formato de genomica del IGTP: ID_SAMPLE_L001_R1.fastq.gz

    Parameters
    ----------
        fastq : str
            Nombre del archivo fastq del que se quiere sacar el read group
    Returns
    -------
        str
            La cadena de read group lista para incrustar en el comando de BWA.
    """
    pass

def getFASTQnames(path) :
    """
    Recoger los nombres de los archivos FASTQ que hay en la ruta especificada.

    Parameters
    ----------
        path : str
            Ruta absoluta donde estan los FASTQ que se van a analizar

    Returns
    -------
        list
            Lista con las rutas absolutas de los FASTQ encontrados en la ruta que se paso como parametro
    """
    files2copy = []
    print("INFO: Recollint el nom dels FASTQ des de {}".format(path))
    for root, dirs, files in os.walk(path) :
        for fic in files :
            # Parche. Se asume que el archivo FASTQ tiene extension .fastq.gz
            aux, extension = os.path.splitext(fic) # Eliminar la primera extension
            name, extension2 = os.path.splitext(aux)
            # Coger los FASTQ que se copiaran en la carpeta de la tanda
            if extension2 == ".fastq" :
                pt = "{}/{}".format(root, fic)
                files2copy.append(pt)
    print("INFO: {} arxius trobats".format(len(files2copy)))

    return files2copy

def getTanda() :
    """
    Busca en la carpeta de analisis cual es el numero de la ultima tanda. Devuelve el numero de la tanda siguiente

    Returns
    -------
        int
            Numero asignado para la siguiente tanda que se va a analizar
    """
    nums = []
    prefijo = len(prefijoTanda)
    for root, dirs, files in os.walk(pathAnalisi) :
        for d in dirs :
            if d.startswith(prefijoTanda) :
                aux = int(d[prefijo:])
                nums.append(aux)
        break
    sig = max(nums) + 1
    return sig

def doListaGenes() :
    """
    Crear el archivo con la lista de genes que hay dentro del manifest
    """
    listaGenes = []
    with open(manifest, "r") as fi :
        for l in fi :
            aux = l.split("\t")[3]
            aux = aux.strip()
            if aux not in listaGenes :
                listaGenes.append(aux)
    with open(genes, "w") as fi :
        fi.write("\n".join(listaGenes))

# TODO: Documentar correctament
def comprobarArchivos() :
    """
    Comprueba si los archivos necesarios para el analisis existen en la ruta especificada en las constantes
    """
    print("INFO: Buscant els arxius necessaris per executar la pipeline")
    if not os.path.isfile(referencia) :
        raise IOError("No se encuentra el genoma de referencia")
    if not os.path.isfile(manifest) :
        raise IOError("No se encuentra el manifest")
    if not os.path.isfile(indels) :
        raise IOError("No se encuentra el archivo para poder realizar el realineamiento de indels")
    if not os.path.isfile(dbsnp) :
        raise IOError("No se encuentra el archivo de SNPs")
    if not os.path.isfile(genes) :
        print("WARNING: No se encuentra el archivo con la lista de genes del manifest. Creando el archivo")
        doListaGenes()


def prepararScript(ruta) :
    """
    Programa principal de la libreria. Prepara el log con todos los comandos necesarios para lanzar la pipeline

    Comandos necesarios:
    * Averiguar el numero de tanda
    * Montar la estructura de la tanda
    * Copiar los FASTQ
    * Crear el bash de analisis
    * Crear, si no existe, la lista de los genes que contiene el manifest (gensAestudi.txt)
    * Crear el log con todos los comandos para cada una de las muestras del panel
    * Ejecutar, si procede el analisis usando la libreria subprocess

    Parameters
    ----------
        ruta : str
            Ruta absoluta donde esta la carpeta con los FASTQ que se van a analizar en esta pipeline
    """
    os.chdir(pathAnalisi) # Cambiar el directorio de trabajo a la carpeta de analisis
    tnd = getTanda() # Crear el nombre de la carpeta donde se guardaran los analisis y el nombre del bash con todos los comandos
    tanda = "{prefijo}{tanda}".format(prefijo = prefijoTanda, tanda = tnd)
    arxiu = "logTanda{tanda}.sh".format(tanda = tnd)

    print("INFO: Els resultats de l'analisi es guardaran en {path}/{tanda}".format(path = pathAnalisi, tanda = tanda))
    comprobarArchivos() # Esta funcion dispara una excepcion en caso de que no se encuentre alguno de los archivos necesarios para el analisis
    fastqs = getFASTQnames(ruta)
    # if len(fastqs) == 0 :
    #     print("ERROR: No s'han trobat arxius FASTQ en {}".format(ruta))
    #     sys.exit(1)
    # else :
    print("INFO: Creant el bash per la tanda {}".format(tnd))
    with open(arxiu, "w") as fi :
        fi.write("#!/bin/bash\n\n") # Shebang del bash
        fi.write("#Referencias usadas en este analisis\n")
        fi.write("ref={}\n".format(referencia))
        fi.write("mani={}\n".format(manifest))
        fi.write("indels={}\n".format(indels))
        fi.write("sites={}\n".format(dbsnp))
        fi.write("gens={}\n\n".format(genes))

        #Crear la funcion que copia los datos (FASTQs) en la carpeta de analisis
        fi.write("function copiar {\n")
        fi.write("\tcd {}\n".format(pathAnalisi))
        fi.write("\tmkdir {tanda} ; cd {tanda}\n\n".format(tanda = tanda))
        fi.write("\techo -e \"################################\\n\\tCopiant dades\\n################################\\n\"\n")
        for f in fastqs :
            patx = f.replace(" ", "\\ ") #Parche para leer los espacios en la terminal bash
            fi.write("\trsync -aP {} .\n".format(patx))

        fi.write("\tmv ../{} .\n".format(arxiu))
        fi.write("}\n\n")

        # TODO Crear les comandes per cadascuna de les etapes de l'analisi
        # TODO: Esta part es com si posara analizar.sh dins del log
        fi.write("function analisi {\n")
        fi.write("\tforward=$1\n\treverse=$2\n\treadgroup=$3\n\talias=$4\n")
        fi.write("\tmkdir $alias\n")
        fi.write("\tcd $alias\n")
        fi.write("\t# Control de calidad. FastQC\n")
        fi.write("\tmkdir fastqc # Carpeta donde se guardara el control de calidad\n")
        # La cadena fastqc tiene una variable (fastq) que se usa para introducir el archivo FASTQ para el analisis
        fi.write("\t" + fastqc.format(fastq = "../$forward") + "\n")
        fi.write("\t" + fastqc.format(fastq = "../$reverse") + "\n")
        fi.write("\trm fastqc/*zip # Eliminar los archivos comprimidos, ya se han descomprimido al finalizar FastQC\n")
        fi.write("# Alineamiento. BWA")
        # La cadena align tiene cuatro variables: rg es para introducir el read group, fw es para el fastq forward, rv es para el fastq reverse y ref es para el genoma de referencia
        fi.write("\t" + bwa.format(rg = "$readgroup", ref = referencia, fw = "../$forward", rv = "../$reverse") + "\n")
        fi.write("\t" + picardSort + "\n")
        fi.write("\t" + picardIndex.format(bam = "bwa.sort.bam") + "\n")
        fi.write("\tmkdir bwaAlign\n")
        fi.write("\tmv bwa.sam *bam *bai bwaAlign/\n")
        # Convertir el bam ordenado en un bed para poder hacer un control de calidad posterior
        fi.write("\tcd bwaAlign\n")
        fi.write("\t" + bedtoolsBam2Bed.format(bam = "bwa.sort.bam") + "\n")
        # Recalibrar las bases
        fi.write("\t" + gatk1.format(bam = "bwa.sort.bam", ref = "$ref", dbsnp = "$sites") + "\n")
        fi.write("\t" + gatk2.format(bam = "bwa.sort.bam", ref = "$ref") + "\n")
        # Aqui puede ir el marcar duplicados, en caso de necesitarse
        fi.write("\t" + markDup.format(bam = "bwa.recal.bam") + "\n")
        fi.write("\t" + picardIndex.format(bam = "bwa.nodup.bam") + "\n")
        fi.write("cd ..")
        # TODO: Estudios de coverage, on target, off target, porcentaje de bases con X coverage...
        fi.write("\n\tCOVERAGE\n")
        fi.write("\testadistiques de l'analisi: on target, off target, % bases amb X coverage, resum dels tests, % duplicats (si cal), grafiques de coverage")
        fi.write("\t" + vc.format(bam = "bwa.nodup.bam") + "\n")
        fi.write("\T$HOME/anpanmds/variantAnnotation.sh variants.vcf")
        fi.write("Script per re-anotar")
        fi.write("Script per filtrar")
        fi.write("}\n\n")

        # TODO: Crear les comandes per analitzar de la mateixa manera a com s'esta fent en els panells d'ALL
