#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import math

import constantes as cte

"""
MAIN: Script que elimina los archivos temporales y no necesarios en un panel que se quiere archivar
"""

#Converteix els bytes en una mesura mes llegible per humans
def convert_size(size_bytes):
    """Convertir los bytes pasados por parametro a formato legible por humanos

    Transforma el numero pasado por parametro a bytes (B), kilobytes (KB), megabytes (MB), gigabytes (GB), terabytes (TB), petabytes (PB), exabytes (EB), zettabytes (ZB), yottabytes (YB)

    Parameters
    ----------
        size_bytes : int
            Numero que se quiere convertir a formato legible por humanos

    Returns
    -------
        str
            Numero en formato legible por humanos (8,3GB, 3B, 1,25MB...)
    """
    ret = ""
    if size_bytes == 0 :
        ret = "0 B"
    else :
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        ret = "{} {}".format(s, size_name[i])
    return ret

def eliminarVariantCalling(ruta) :
    """Eliminar los archivos temporales del variant calling

    Elimina los archivos temporales de las carpetas de variant calling en la tanda pasada por parametro. Estos archivos temporales son:
        * cand.reanno.tsv, highMAF.reanno.tsv, raw.hg19_multianno.txt, variants.stats.txt, conseq.reanno.tsv, lowVAF.reanno.tsv, raw.av, raw.reanno.tsv si el variant calling se ha hecho usando
        Mutect2

    Parameters
    ----------
        ruta : str
            Nombre de la tanda que se quiere archivar
    """
    print("INFO: Eliminando temporales de la carpeta de variantes")
    cont = 0
    pes = 0
    # Recoger los directorios (muestras) que se han hecho en la tanda
    for root, dirs, files in os.walk(ruta) :
        break

    for d in dirs :
        path = "{root}/{samp}/variantCalling".format(root = ruta, samp = d)
        if os.path.isdir(path) :
            arxius = os.listdir(path)
            # Eliminar los temporales de un variant calling hecho usando VarScan2
            if "varscan.vcf" in arxius :
                for a in arxius :
                    if a == "bwa.pileup" :
                        pes += os.path.getsize("{dir}/bwa.pileup".format(dir = path))
                        cont += 1
                        os.remove("{dir}/bwa.pileup".format(dir = path))
                    elif a.startswith("filtro") and not a.endswith(".allInfo") :
                        pes += os.path.getsize("{dir}/{file}".format(dir = path, file = a))
                        cont += 1
                        os.remove("{dir}/{file}".format(dir = path, file = a))
            # Eliminar los archivos temporales de un variant calling hecho usando Strelka2
            if "strelka2.vcf" in arxius :
                print("WARNING: Opcion no implementada todavia")
            # Eliminar los archivos temporales de un variant calling hecho usando Mutect2
            if "mutect.vcf" in arxius :
                eliminar = ["cand.reanno.tsv", "highMAF.reanno.tsv", "raw.hg19_multianno.txt", cte.variantstats, "conseq.reanno.tsv", "lowVAF.reanno.tsv", "raw.av", "raw.reanno.tsv"]
                for a in arxius :
                    if a in eliminar :
                        pes += os.path.getsize("{dir}/{arx}".format(dir = path, arx = a))
                        cont += 1
                        os.remove("{dir}/{arx}".format(dir = path, arx = a))


    print("INFO: {} archivos eliminados. {} espacio liberado".format(cont, convert_size(pes)))

def eliminarAliniament(ruta) :
    """Eliminar los archivos temporales del alineamiento

    Elimina los archivos temporales de las carpetas de alineamiento de la tanda pasada por parametro. Estos archivos temporales son bwa.sam, bwa.sort.bam, bwa.sort.bai, bwa.bed y
    recaldata.table

    Parameters
    ----------
        ruta : str
            Nombre de la tanda que se quiere archivar
    """
    print("INFO: Eliminando bams intermedios")
    cont = 0 # Contador de arxius elminats
    pes = 0
    arxius = ["bwa.sam", "bwa.sort.bam", "bwa.sort.bai", "bwa.bed", "recaldata.table"] # Lista d'arxius a eliminar
    # Recollir els directoris de cadascuna de les mostres en la tanda
    for root, dirs, files in os.walk(ruta) :
        break

    # En cadascuna de les mostres, eliminar els arxius bwa.sam, bwa.sort.bam, bwa.sort.bai i indelsGATK.list
    for d in dirs :
        path = "{root}/{samp}/alignment".format(root = ruta, samp = d)
        for a in arxius :
            arx = "{}/{}".format(path, a)
            if os.path.isfile(arx) :
                pes += os.path.getsize(arx)
                os.remove(arx)
                cont += 1
    print("INFO: {} bams eliminados. {} espacio liberado".format(cont, convert_size(pes)))


def eliminarFASTQ(ruta) :
    """Eliminar los archivos FASTQ de la tanda que se quiere archivar

    Elimina los archivos con extension .fastq.gz de la carpeta de tanda pasada por parametro.

    Parameters
    ----------
        ruta : str
            Nombre de la tanda que se quiere archivar
    """
    print("INFO: Eliminando archivos FASTQ")
    cont = 0
    pes = 0
    for root, dirs, files in os.walk(ruta) :
        for f in files :
            if f.endswith("fastq.gz") :
                cont += 1
                pes += os.path.getsize("{path}/{arxiu}".format(path = ruta, arxiu = f))
                os.remove("{path}/{arxiu}".format(path = ruta, arxiu = f))

    print("INFO: {} archivos eliminados. {} espacio liberado".format(cont, convert_size(pes)))

def main(tanda = "") :
    """Programa principal

    En caso de no recibir el nombre de una tanda en la ejecucion del programa, pregunta al usuario por le numero de tanda que se quiere eliminar. Una vez comprobado que la carpeta con la tanda
    existe, invoca a eliminarFASTQ, eliminarAliniament y eliminarVariantCalling para que eliminen los datos temporales de las carpetas correspondientes
    """
    root = "/home/ffuster/panalisi/resultats"
    if tanda == "" :
        tanda = input("REQUEST: Numero de tanda que se quiere limpiar: ")

    try :
        t = int(tanda)
        tanda = "tanda{}".format(t)
    except ValueError :
        print("ERROR: El numero de tanda no es un numero. Valor introducido: {}".format(tanda))
        sys.exit(1)

    path = "{root}/{tanda}".format(root = root, tanda = tanda)
    if os.path.isdir(path) :
        eliminarFASTQ(path)
        eliminarAliniament(path)
        eliminarVariantCalling(path)
    else :
        print("ERROR: La carpeta {} no existe".format(path))

if __name__ == "__main__" :
    if len(sys.argv) > 1 :
        main(sys.argv[1])
    else :
        main()
