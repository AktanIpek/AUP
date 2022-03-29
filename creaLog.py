#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MAIN: Funciones para crear el log de analisis de los paneles
"""

"""
FUNCTIONS:
    prepararScript - Crea el bash con todos los comandos que se van a usar en el análisis del panel
    extraerRG - Extrae el Read Group de los FASTQ
    FALTEN FUNCIONS PER POSAR ACI
"""
import os
import re
import sys

import constantes as cte
import getCommands as cmd
import manifestOp as op

def extraerRG(fastq) :
    """
    Extrae el Read Group de un archivo FASTQ.

    Extrae el identificador de muestra y el numero de muestra a partir del nombre de un archivo FASTQ pasado por parametro. Con estos datos construye los parametros necesarios
    para lanzar el analisis de la muestra. Estos parametros son: nombre del FASTQ R1, nombre del FASTQ R2, Read Group, Alias para la muestra
    Se espera el formato de genomica del IGTP: ID_SAMPLE_L001_R1.fastq.gz

    Parameters
    ----------
        fastq : str
            Nombre del archivo fastq del que se quiere sacar el read group
    Returns
    -------
        str
            La cadena de read group lista para incrustar en el comando de BWA. Si no se reconoce el formato, devolvera "No valido"
        str
            El identificador de la muestra. Si no se reconoce el formato, devolvera "No valido"
    """
    # Formato esperado ID_SAMPLE_L001_R1.fastq.gz
    aux = fastq.split("_")
    reg = "_S[\d]+_L001_R[\d]?_001\.fastq\.gz"
    if re.search(reg, fastq) :
        rgid = aux[0]
        sample = aux[1]
        fq1 = "{id}_{samp}_L001_R1_001.fastq.gz".format(id = rgid, samp = sample)
        fq2 = "{id}_{samp}_L001_R2_001.fastq.gz".format(id = rgid, samp = sample)
        rg = "\"@RG\\tID:{id}\\tSM:{samp}\\tPL:ILLUMINA\"".format(id = rgid, samp = sample)
        whole = "{fq1} {fq2} {rg} {alias}".format(fq1 = fq1, fq2 = fq2, rg = rg, alias = rgid)
    else :
        whole = "No valido"
        rgid = "No valido"
    return whole, rgid

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
    print("INFO: Recogiendo el nombre de los FASTQ en {}".format(path))
    for root, dirs, files in os.walk(path) :
        for fic in files :
            # Parche. Se asume que el archivo FASTQ tiene extension .fastq.gz
            aux, extension = os.path.splitext(fic) # Eliminar la primera extension
            name, extension2 = os.path.splitext(aux)
            # Coger los FASTQ que se copiaran en la carpeta de la tanda
            if extension2 == ".fastq" :
                pt = "{}/{}".format(root, fic)
                files2copy.append(pt)
    print("INFO: {} archivos encontrados".format(len(files2copy)))

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
    prefijo = len(cte.prefijoTanda)
    for root, dirs, files in os.walk(cte.workindir) :
        for d in dirs :
            if d.startswith(cte.prefijoTanda) :
                aux = int(d[prefijo:])
                nums.append(aux)
        break
    sig = max(nums) + 1
    return sig

def comprobarArchivos() :
    """Comprobar que existen los archivos externos para el analisis

    Comprueba si los archivos necesarios para el analisis existen en la ruta especificada en las constantes. Estos archivos son: el genoma de referencia, el manifest (regiones de interes
    en las que se ha focalizado el panel), el manifest comprimido y su indice correspondiente (para analizar el panel usando Strelka2), el archivo de SNPs (para recalibrar bases y para
    el variant calling usando Mutect2) y la lista de genes en los que se ha focalizado el panel (para analisis de coverage).

    Raises
    ------
        IOError
            Si alguno de los archivos no existe lanzara dicha excepcion
    """
    print("INFO: Buscando los archivos necesarios para ejecutar la pipeline")
    if not os.path.isfile(cte.genoma_referencia) :
        raise IOError("No se encuentra el genoma de referencia")
    if not os.path.isfile(cte.manifest) :
        raise IOError("No se encuentra el manifest. Buscando en {}".format(cte.manifest))
    else : #Strelka2 quiere que el bam este comprimido e indexado. Comprobar si estas archivos existen
        if not os.path.isfile(cte.gzmanifest) :
            raise IOError("ERROR: No se encuentra el bgzip del manifest, necesario para Strelka2. Buscado como {}".format(cte.gzmanifest))
        if not os.path.isfile(cte.manifestidx) :
            raise IOError("ERROR: No se encuentra el indice del manifest, necesario para Strelka2. Buscado como {}".format(cte.manifestidx))
    if not os.path.isfile(cte.dbsnp) :
        raise IOError("No se encuentra el archivo de SNPs. Buscado como {}".format(cte.dbsnp))
    if not os.path.isfile(cte.genes) :
        print("WARNING: No se encuentra el archivo con la lista de genes del manifest. Creando el archivo")
        op.doListaGenes(cte.manifest, cte.genes)

def encontrar(fq, lista) :
    """Encontrar un fastq en la lista con los paths absolutos de fastqs

    Parameters
    ----------
        fq : str
            Archivo fastq que se quiere buscar el fastq
        lista : list
            Lista de paths absolutos donde se busca el fastq

    Returns
    -------
        str, None
            Ruta absoluta del fastq que se esta buscando
            None en caso de no encontrar el fastq en la lista
    """
    ret = None
    for l in lista :
        if l.endswith(fq) :
            ret = l
            break

    return ret

def prepararPanel(ruta, acciones) :
    """
    Programa principal de la libreria. Prepara el log con todos los comandos necesarios para lanzar la pipeline

    Comandos necesarios:
    * Averiguar el numero de tanda
    * Montar la estructura de la tanda
    * Copiar los FASTQ
    * Crear el bash de analisis. Dependera de la lista de acciones que se han determinado
    * Crear, si no existe, la lista de los genes que contiene el manifest (gensAestudi.txt)
    * Crear el log con todos los comandos para cada una de las muestras del panel

    Parameters
    ----------
        ruta : str
            Ruta absoluta donde esta la carpeta con los FASTQ que se van a analizar en esta pipeline
        acciones : list
            Lista de acciones que se pueden agregar al bash. Valores aceptados: ["copiar","fastqc", "aln", "recal", "mdups", "bamqc", "coverage", "strelkaGerm", "mutectGerm", "vanno",
            "filtrar", "excel"]
    """
    os.chdir(cte.workindir) # Cambiar el directorio de trabajo a la carpeta de analisis
    tnd = getTanda() # Crear el nombre de la carpeta donde se guardaran los analisis y el nombre del bash con todos los comandos
    tanda = "{prefijo}{tanda}".format(prefijo = cte.prefijoTanda, tanda = tnd)
    arxiu = "logTanda{tanda}.sh".format(tanda = tnd)

    print("INFO: Los resultados del analisis se guardaran en {path}/{tanda}".format(path = cte.workindir, tanda = tanda))
    comprobarArchivos() # Esta funcion dispara una excepcion en caso de que no se encuentre alguno de los archivos necesarios para el analisis
    fastqs = getFASTQnames(ruta)
    if len(fastqs) == 0 :
        print("ERROR: No se han encontrado archivos FASTQ en {}".format(ruta))
        sys.exit(1)
    else :
        print("INFO: Creando el bash para la tanda {}".format(tnd))
        with open(arxiu, "w") as fi :
            fi.write("#!/bin/bash\n\n") # Shebang del bash
            fi.write("#Referencias usadas en este analisis\n")
            fi.write("ref={}\n".format(cte.genoma_referencia))
            fi.write("mani={}\n".format(cte.manifest))
            fi.write("gzmani={}\n".format(cte.gzmanifest))
            fi.write("sites={}\n".format(cte.dbsnp))
            fi.write("gens={}\n\n".format(cte.genes))
            if "copiar" in acciones :
                #Crear la funcion que copia los datos (FASTQs) en la carpeta de analisis
                fi.write("function copiar {\n")
                fi.write("\tcd {}\n".format(cte.workindir))
                fi.write("\tmkdir {tanda} ; cd {tanda}\n\n".format(tanda = tanda))
                fi.write("\techo -e \"################################\\n\\tCopiant dades\\n################################\\n\"\n")
                for f in fastqs :
                    patx = f.replace(" ", "\\ ") #Parche para leer los espacios en la terminal bash
                    fi.write("\trsync -aP {} .\n".format(patx))

                fi.write("\trsync -aP {} .\n".format("$gens"))
                fi.write("\tmv ../{} .\n".format(arxiu))
                fi.write("}\n\n")
            else :
                fi.write("# Crear la estructura de la tanda\n")
                fi.write("cd {}\n".format(cte.workindir))
                fi.write("mkdir {tanda} ; cd {tanda}\n".format(tanda = tanda))
                fi.write("rsync -aP {} .\n".format("$gens"))
                fi.write("mv ../{} .\n".format(arxiu))

            fi.write("function analisi {\n")
            fi.write("\tforward=$1\n\treverse=$2\n\treadgroup=$3\n\talias=$4\n")
            fi.write("\techo -e \"################################\\n\\tAnalitzant $alias\\n################################\\n\"\n")
            fi.write("\tmkdir $alias\n")
            fi.write("\tcd $alias\n")
            if "fastqc" in acciones :
                fi.write("\n\t# Control de calidad. FastQC\n")
                fi.write("\tmkdir fastqc # Carpeta donde se guardara el control de calidad\n")
                # Recoger la orden para invocar fastqc usando la libreria de comandos
                if "copiar" in acciones : # Si se han copiado los datos, el path que se pasa a la funcion es relativo.
                    fi.write("\t" + cmd.getFastQC("../$forward", "fastqc") + "\n")
                    fi.write("\t" + cmd.getFastQC("../$reverse", "fastqc") + "\n")
                else : # En caso contrario el path es absoluto
                    fi.write("\t" + cmd.getFastQC("$forward", "fastqc") + "\n")
                    fi.write("\t" + cmd.getFastQC("$reverse", "fastqc") + "\n")
                fi.write("\trm fastqc/*zip # Eliminar los archivos comprimidos, ya se han descomprimido al finalizar FastQC\n")
            if "aln" in acciones :
                fi.write("\n\t# Alineamiento. BWA\n")
                # La orden align tiene cuatro variables: rg es para introducir el read group, fw es para el fastq forward, rv es para el fastq reverse y ref es para el genoma de referencia
                if "copiar" in acciones : # Si se han copiado los FASTQ al directorio de la tanda, el path enviado a la funcion sera un path relativo
                    fi.write("\t" + cmd.getAln("$readgroup", "$ref", "../$forward", "../$reverse", "bwa.sam") + "\n")
                else : # Si no se han copiado los FASTQ, la ruta que se pasa a la funcion es absoluta
                    fi.write("\t" + cmd.getAln("$readgroup", "$ref", "$forward", "$reverse", "bwa.sam") + "\n")
                fi.write("\t" + cmd.getPcSort("bwa.sam", "bwa.sort.bam") + "\n")
                fi.write("\t" + cmd.getPcIndex("bwa.sort.bam") + "\n")
                fi.write("\tmkdir alignment\n")
                fi.write("\tmv bwa.sam *bam *bai alignment/\n")
            fi.write("\tcd alignment\n")
            # Convertir el bam ordenado en un bed para poder hacer un control de calidad posterior
            if "bamqc" in acciones :
                fi.write("\t" + cmd.getBam2bed("bwa.sort.bam", "bwa.bed") + "\n")
            # Recalibrar las bases
            if "recal" in acciones :
                fi.write("\n\t# Post-Alineamiento. GATK\n")
                # GATKrecal devuelve dos ordenes, separadas por \n. Como queremos que se tabule tambien la segunda linea, se reemplaza el \n por \n + \t
                fi.write("\t" + cmd.getGATKrecal("bwa.sort.bam", "$ref", "$sites", "bwa.recal.bam", "$mani").replace("\n", "\n\t") + "\n")

            # Marcar duplicados
            if "mdups" in acciones :
                fi.write("\t" + cmd.getPcMarkduplicates("bwa.recal.bam", "bwa.nodup.bam") + "\n")
                fi.write("\t" + cmd.getPcIndex("bwa.nodup.bam") + "\n")
            fi.write("\tcd ..\n")
            # Estudios de coverage, on target, off target, porcentaje de bases con X coverage...
            if "coverage" in acciones :
                fi.write("\n\t# Control de calidad del alineamiento y estudio de coverage\n")
                fi.write("\t" + cmd.getCoverageAll("$mani","alignment/bwa.recal.bam", cte.covarx) + "\n")
                fi.write("\t" + cmd.getCoverageBase("$mani", "alignment/bwa.recal.bam", "coverageBase.txt") + "\n")
                fi.write("\tgrep '^all' {} > coverageAll.txt\n".format(cte.covarx))
                fi.write("\trm {}\n".format(cte.covarx))
                fi.write("\tRscript {}/coveragePanells.R\n".format(cte.scriptdir))
                fi.write("\tmkdir coverage\n")
                fi.write("\tmv *png coverageAll.txt coverageBase.txt coverage/\n")
            if "bamqc" in acciones :
                fi.write("\tpython3 {}/bamQC.py\n".format(cte.scriptdir)) # Hay una opcion de lanzar pctDups (calcular porcentaje de duplicados) en caso de exomas
            # Variant calling. La carpeta donde se guardan los datos se llama variantCalling. En caso de queren cambiarse, modificar las dos siguientes lineas
            if "strelkaGerm" in acciones :
                fi.write("\n\t# Variant calling. Strelka2\n")
                if "mdups" in acciones :
                    fi.write("\t" + cmd.getStrelka2("alignment/bwa.nodup.bam", "$ref", "variantCalling", "$gzmani", "variantCalling").replace("\n", "\n\t") + "\n")
                elif "recal" in acciones:
                    fi.write("\t" + cmd.getStrelka2("alignment/bwa.recal.bam", "$ref", "variantCalling", "$gzmani", "variantCalling").replace("\n", "\n\t") + "\n")
                else :
                    fi.write("\t" + cmd.getStrelka2("alignment/bwa.sort.bam", "$ref", "variantCalling", "$gzmani", "variantCalling").replace("\n", "\n\t") + "\n")
                fi.write("\trsync -aP results/variants/variants.vcf.gz .\n")
                fi.write("\tgunzip variants.vcf.gz\n")
                fi.write("\tmv variants.vcf strelka2.vcf")
                # Anotacion de variantes usando ANNOVAR
                if "vanno" in acciones :
                    fi.write("\n\t# Anotacion y filtrado de variantes. ANNOVAR y myvariant.info\n")
                    fi.write("\t" + cmd.getANNOVAR("strelka2.vcf", "raw").replace("\n", "\t\n") + "\n")
                # Re-anotacion y filtrado de variantes usando myvariant.info
                if "filtrar" in acciones :
                    fi.write("\tpython3 {wd}/filtStrelka.py {input} {samplename}".format(wd = cte.scriptdir, input = "raw.hg19_multianno.txt", samplename = "$alias"))
            elif "mutectGerm" in acciones :
                fi.write("\n\t#Variant calling. Mutect2\n")
                if "mdups" in acciones :
                    fi.write("\t" + cmd.getMutect2("alignment/bwa.nodup.bam", "$ref", "$sites", "mutect", "$mani").replace("\n", "\n\t") + "\n")
                elif "recal" in acciones :
                    fi.write("\t" + cmd.getMutect2("alignment/bwa.recal.bam", "$ref", "$sites", "mutect", "$mani").replace("\n", "\n\t") + "\n")
                else :
                    fi.write("\t" + cmd.getMutect2("alignment/bwa.sort.bam", "$ref", "$sites", "mutect", "$mani").replace("\n", "\n\t") + "\n")
                # Anotacion de variantes usando ANNOVAR
                if "vanno" in acciones :
                    fi.write("\n\t# Anotacion y filtrado de variantes. ANNOVAR y myvariant.info\n")
                    temp = cmd.getANNOVAR("mutect.revised.vcf", "raw").split("\n")
                    fi.write("\t" + temp[0] + "\n")
                    fi.write("\t" + temp[1] + "\n")
                # Re-anotacion y filtrado de variantes usando myvariant.info
                if "filtrar" in acciones :
                    if "mutectGerm" in acciones :
                        fi.write("\tpython3 {wd}/filtMutect.py {input} {samplename}\n".format(wd = cte.scriptdir, input = "raw.hg19_multianno.txt", samplename = "$alias"))


            # Juntar los resultados obtenidos en un Excel
            if "excel" in acciones :
                fi.write("\tpython3 {wd}/data2excel.py {output}\n".format(wd = cte.scriptdir, output = "$alias"))
            fi.write("\tcd {}/{}\n".format(cte.workindir, tanda))

            fi.write("}\n\n")

            #Crear los comandos para lanzar las funciones
            if "copiar" in acciones :
                fi.write("copiar\n")
            hechos = []
            for f in fastqs :
                params, id = extraerRG(os.path.basename(f))
                if params == "No valido" :
                    print("WARNING: Formato de FASTQ no reconocido para el archivo: {}. Se debera montar la orden para analizar manualmente".format(f))
                else :
                    # Convertir las rutas de los FASTQ en rutas absolutas
                    if not "copiar" in acciones :
                        aux =  params.split(" ")
                        aux[0] = encontrar(aux[0], fastqs)
                        aux[1] = encontrar(aux[1], fastqs)
                        params = " ".join(aux)
                    if id not in hechos :
                        fi.write("analisi {params}\n".format(params = params))
                        hechos.append(id)
            # Hacer un informe de calidad del panel analizado
            fi.write("cd {}/{}\n".format(cte.workindir, tanda))
            fi.write("python3 {wd}/informeQCtanda.py".format(wd = cte.scriptdir))
        print("INFO: Log guardado como {}/{}".format(cte.workindir, arxiu))
        os.chmod(arxiu, 0o754) # Dar permiso de ejecuion para el propietario, lectura y escritura para el grupo, y lectura para el resto de usuarios
