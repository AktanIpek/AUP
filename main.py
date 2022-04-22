#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MAIN: Programa principal. Muestra los pasos a seguir para poder hacer el analisis automatico de paneles en SMD. Usa la libreria creaLog para ejecutar el analisi
"""

import os
import subprocess
import sys

import bamQC as bq
import constantes as cte
import creaLog as cl
import data2excel as xls
import filtStrelka as fis
import filtMutect as fim
import getCommands as gc
import informeQC as qc
import informeQCtanda as globalqc
import manifestOp as op
import moverDatos as mv

def reanalizar() :
    """Reanalizar una muestra sin borrar lo que ya esta guardado"""
    samp = input("INPUT: Identificador de la muestra a reanalizar: ")
    # Buscar la muestra en el directorio de trabajo usando el comando find de bash
    cmd = "find {wd} -name {smp}*fastq.gz".format(smp = samp, wd = cte.workindir)
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    res = out.decode()
    if res == "" :
        print("INFO: No se ha encontrado la muestra en {}".format(cte.workindir))
    else :
        # Convertir los resultados a una lista
        aux = res.split("\n")
        # Si se encuentran, recoger el directorio donde esta el fastq y lanzar un analisis con dicha muestra
        ruta = os.path.dirname(aux[0])
        acciones = custom()
        if "copiar" in acciones : # Evitar que se copien los FASTQ
            acciones.remove("copiar")

        lanzarPanel(ruta, acciones)

        # Buscar el log que se ha creado al lanzar el panel
        for root, dirs, filenames in os.walk(cte.workindir, topdown = True, ) :
            break

        for f in filenames :
            if f.startswith("logTanda") :
                logf = f
                break
        # Modificar el log para eliminar las otras muestras que podria haber en el directorio
        os.chdir(cte.workindir)
        with open(logf, "r") as fi :
            cont = fi.readlines()
        for c in range(len(cont)) :
            if cont[c].startswith("mkdir") :
                cont[c] = "mkdir {smp} ; cd {smp}\n".format(smp = samp) # Modificar la linea del log que crea la carpeta de la tanda. Se crea una carpeta con el nombre de la muestra
            if cont[c].startswith("mv") :
                cont[c] = "mv ../log{}.sh .\n\n".format(samp) # Como el nombre del log se va modificar posteriormente. Cambiar el nombre del log dentro del log propiamente dicho
            if cont[c].startswith("cd /") :
                cont[c] = "" # Eliminar la ultima linea de la funcion analisi puesto que apuntaria a la carpeta de la tanda y esta no se ha creado

        # Eliminar los analisis de los FASTQ que no son de la muestra que se ha pedido reanalizar
        newCont = [x for x in cont if not x.startswith("analisi") or (x.startswith("analisi") and x.find(samp) > -1)]
        newLog = "log{}.sh".format(samp)
        # Guardar los cambios en el archivo
        with open(logf, "w") as fi :
            for c in newCont :
                fi.write(c)
        os.rename(logf, newLog) # Cambiar el nombre logTanda__.sh por el nombre de la muestra
        print("INFO: Cambiado el nombre de {} por {}".format(logf, newLog))

def vcf() :
    """Anotar y filtrar un vcf. Guardar los datos en un excel

    Pide al usuario la ruta de un archivo vcf. Anota y filtra los datos de dicho excel. Finalmente guarda todo en un excel. Todos los datos se guardan en la carpeta donde esta el vcf
    """
    ruta = input("INPUT: Introducir el path absoluto del vcf: ")
    name = input("INPUT: Introducir el nombre de la muestra: ")
    hg = input("INPUT: Introducir el genoma de referencia usado (hg19, hg38): ")
    # Comprobar que tipo de variant calling se ha hecho
    vcal = None
    format = "vcf4"
    # Buscar Mutect2, VarScan2, configureStrelka para saber cual de los variant callers se ha introducido
    with open(ruta, "r") as fi :
        for l in fi :
            # Leer solo la cabecera del vcf para determinar el variant caller y si el vcf es de comparacion somatica o somatico/germinal sin comparacion
            if l.startswith("#") :
                # Comprobar que la muestra es somatica y hace falta cambiar el parametro -format de ANNOVAR a vcf4old
                if l.startswith("#CHROM") :
                    if len(l.split("\t")) == 11 :
                        format = "vcf4old"

                if "Mutect2" in l :
                    vcal = "Mutect2"
                elif "VarScan2" in l :
                    vcal = "VarScan2"
                elif "configureStrelka" in l :
                    vcal = "Strelka2"
            else :
                break
    if vcal == None :
        print("ERROR: No se pudo determinar el variant caller del vcf")
    else :
        print("INFO: Anotando VCF")
        lst = None
        # Cambiar el directorio de trabajo a la carpeta donde esta el vcf
        wd = os.path.dirname(ruta)
        os.chdir(wd)
        # Anotar el vcf. Comprobar que no se haya anotado antes
        arx = "{}.{}_multianno.txt".format(name, hg)
        if not os.path.isfile(arx) :
            if hg == "hg19" :
                lst = gc.getANNOVAR(ruta, name, "hg19", format)
            elif hg == "hg38" :
                lst = gc.getANNOVAR(ruta, name, "hg38", format)
            else :
                raise ValueError("ERROR: Genoma de referencia no soportado")

            if lst != None :
                for c in lst.split("\n") :
                    proc = subprocess.Popen(c, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    out, err = proc.communicate()

        # Ejecutar filtMutect, filtStrelka, dependiendo del variant caller encontrado
        if vcal == "Strelka2" :
            fis.main(arx, name)
            xls.crearExcel(name)
        elif vcal == "Mutect2" :
            fim.main(arx, name)
            xls.crearExcel(name)
        elif vcal == "VarScan2" :
            print("Pendiente hacer filtrado de VarScan2")

def bamQC(ruta = None) :
    """Calcula los parametros de calidad de un bam"""
    if ruta == None :
        ruta = input("INPUT: Introducir el path absoluto del bam a analizar: ")

    os.chdir(os.path.dirname(ruta))
    bq.bed = "bwa.bed"
    bq.bam = "bwa.recal.bam"
    bq.fastqc = "../fastqc"
    bq.main()
    # El script bamQC.py crea un archivo de texto, llamado alnQC.txt, con un JSON con los datos de interes
    with open(cte.qcaln, "r") as fi :
        txt = fi.read()
    qc = eval(txt)
    for k, v in qc.items() :
        if k == "ON" or k == "OFF":
            print("{} - {} ({:.2f} %)".format(k, v, 100*float(v)/float(qc["BAM"])))
        else :
            print("{} - {}".format(k, v))
    os.remove(cte.bedoutput)
    os.remove(cte.qcaln)

def custom() :
    """Crear un analisis customizado usando un wizard"""
    """
    OPCIONES YA CONTEMPLADAS EN CREAR LOG
    copiar
    fastqc
    aln
    recal
    bamqc
    mdups
    coverage
    strelkagerm
    mutectgerm
    vanno
    filtrar
    excel
    """
    ordenes = []
    print("\n\t------------------------------------------------\n\t\tAnalisis personalizado del panel\n\t------------------------------------------------\n")

    if input("Copiar los fastq? (S/N) ").lower() == "s" :
        ordenes.append("copiar")

    if input("Control de calidad de los fastq? (S/N) ").lower() == "s" :
        ordenes.append("fastqc")

    if input("Alinear? (S/N) ").lower() == "s" :
        ordenes.append("aln")
        if input("Recalibrar bases? (S/N) ").lower() == "s" :
            ordenes.append("recal")
        if input("Marcar duplicados? (S/N) ").lower() == "s" :
            ordenes.append("mdups")
        if input("Control de calidad del bam? (S/N) ").lower() == "s" :
            ordenes.append("bamqc")
        if input("Calculo de coverage del bam? (S/N) ").lower() == "s" :
            ordenes.append("coverage")
        aux = input("Con que programa hacer el variant calling? Opciones disponibles (strelka_germinal, mutect_germinal). En caso de no querer variant calling, escribir 'n' ")
        if aux.lower() != 'n' :
            aux = aux.replace("_germinal", "germ")
            ordenes.append(aux)
            if input("Anotar variantes usando ANNOVAR? (S/N) ").lower() == "s" :
                ordenes.append("vanno")
                if input("Filtrar variantes? (S/N) ").lower() == "s" :
                    ordenes.append("filtrar")
                    if input("Convertir los datos en excel? (S/N) ").lower() == "s" :
                        ordenes.append("excel")
    print("INFO: Se va a crear un log que ejecutara los siguientes pasos: {}".format(", ".join(ordenes)))
    return ordenes

def anotarManifest() :
    ruta = input("INPUT: Introducir ruta absolute del manifest a anotar: ")
    op.anotarManifest(ruta)

def hacerInforme(ruta) :
    try :
        int(ruta) # Si la ruta es un numero, es que se quiere hacer el informe de todas las muestras dentro de una tanda
        tanda = "{}/tanda{}".format(cte.workindir, ruta)
        if os.path.isdir(tanda) :
            for root, dirs, files in os.walk(tanda) :
                break
            for d in dirs :
                print("INFO: Creando informe para {}".format(d))
                os.chdir("{}/{}".format(tanda, d))
                qc.crearInforme()
    except ValueError :
        cmd = "find {wd} -name {smp}".format(smp = ruta, wd = cte.workindir)
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = proc.communicate()
        res = out.decode()
        if res == "" :
            print("INFO: No se ha encontrado {} en {}".format(ruta, cte.workindir))
        else :
            res = res.strip()
            print("INFO: Creando informe para la muestra {}".format(res))
            os.chdir(res)
            qc.crearInforme()

def lanzarPanel(ruta, opciones) :
    cl.prepararPanel(ruta, opciones)

def GUI() :
    """
    Menu de interaccion con el usuario. Muestra las opciones de analisis disponibles
    """
    #os.system('clear')
    print("\t\t------------------------------------------------------\n\t\t\tAnalisis aUtomatico de Paneles\n\t\t------------------------------------------------------\n\nOpciones")
    print("1. Analisis tipico del panel")
    print("2. Analisis custom del panel")
    print("3. Analizar una unica muestra")
    print("4. Control de calidad de un bam")
    print("5. Anotar y filtrar un vcf")
    print("6. Reanalizar una muestra de una tanda, conservando el analisis previo")
    print("7. Anotar un manifest")
    print("8. Crear un informe de la calidad de los FASTQ, el alineamiento y el coverage")
    print("9. Crear un informe de la tanda")
    print("0. Copiar datos de un panel a otra ubicacion")
    opt = input("INPUT: Numero de opcion: ")
    # Comprobar si la opcion es un numero
    try :
        opt = int(opt)
    except ValueError :
        print("ERROR: La opcion no es un numero")
        sys.exit(1)
    # Analizar un panel de forma clasica/estandar
    if opt == 1 :
        ruta = input("INPUT: Introducir el path absoluto de la carpeta donde estan los FASTQ a analizar: ")
        lanzarPanel(ruta, ["copiar","fastqc", "aln", "recal", "bamqc", "coverage", "mutectGerm", "vanno", "filtrar", "excel"])
    # Analizar el panel usando una pipeline escogida por el usuario
    elif opt == 2 :
        ruta = input("INPUT: Introducir el path absoluto de la carpeta donde estan los FASTQ a analizar: ")
        opciones = custom()
        lanzarPanel(ruta, opciones)
    elif opt == 3 :
        ruta = input("INPUT: Introducir la carpeta donde estan los fastq de la muestra a analizar: ")
        opciones = custom()
        lanzarPanel(ruta, opciones)
    elif opt == 4 :
        ruta = input("INPUT: Introducir el path absoluto del bam a analizar: ")
        bamQC(ruta)
    elif opt == 5 :
        vcf()
    elif opt == 6 :
        reanalizar()
    elif opt == 7 :
        ruta = input("INPUT: Introducir la ruta del manifest: ")
        op.anotarManifest(ruta)
    elif opt == 8 :
        ruta = input("INPUT: Muestra o numero de tanda en la que realizar el informe: ")
        hacerInforme(ruta)
    elif opt == 9 :
        print("\n")
        globalqc.main()
    elif opt == 0 :
        print("\n")
        mv.main()
    else :
        print("ERROR: Opcion no valida")
        sys.exit(1)

if __name__ == "__main__" :
    GUI()
