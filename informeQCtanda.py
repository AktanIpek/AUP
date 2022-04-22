#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys

import constantes as cte
import vcfQC

# Constantes locales
imgFolder = "img" # Nombre de la carpeta donde se guardaran las imagenes generadas por el script de R

def datosPlantilla() :
    """La plantilla necesita
        * una tabla de variantes (formato <tr><td>CROMOSOMA</td><td>POSICION</td><td>REF</td><td>ALT</td><td>GEN</td><td>VECES</td>),
        * lista con las imagenes de los coverages de cada gen (formato <img src='IMAGEN'>)
        * lista con los porcentajes de bases que tiene cada muestra (formato <img src='IMAGEN')
    """
    # Crear la tabla de variantes
    tabVar = ""
    fullpath = os.getcwd().split("/")[1:-1]
    cmd = "cut -f1,2,4,5,7 /{}/*/variantCalling/raw.hg19_multianno.txt | sort -k1,1 -V | grep -v Chr | uniq -c | sort -k1 -k2,1 -V".format("/".join(fullpath))
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    fils = out.decode().split("\n")
    for f in fils :
        tmp = f.split("\t")
        aux = tmp[0].split()
        if len(aux) == 2 :
            times, chr = aux
            pos = tmp[1]
            ref = tmp[2]
            alt = tmp[3]
            gen = tmp[4]
            tabVar += "<tr><td>chr{crom}</td><td>{pos}</td><td>{ref}</td><td>{alt}</td><td>{gen}</td><td>{times}</td></tr>\n".format(crom = chr, pos = pos, ref = ref, alt = alt, gen = gen, times = times)
    # Crear las lista de imagenes con los coverages. Las imagenes que empiezan por cov* son coverages por base en cada gen. Las que acaban en _coverage.png son porcentajes
    files = os.listdir(os.getcwd())
    files.sort()
    covs = ""
    samps = ""
    for f in files :
        if f.endswith(".png") : # Es una imagen
            if f.endswith("_coverage.png") :
                samps += "<img src='{}/{}'>\n".format(imgFolder, f)
            elif f.startswith("cov") :
                covs += "<img src='{}/{}'>\n".format(imgFolder, f)

    return tabVar, covs, samps

def recogerDatos(ruta = "./") :
    if ruta == "./" :
        print("INFO: Realizando control de calidad en {}".format(os.getcwd()))
    else :
        print("INFO: Realizando control de calidad en {}".format(ruta))
    # Leer las carpetas con los nombres de las muestras
    for root, dirs, files in os.walk(ruta) :
        break

    print("INFO: {} muestras encontradas".format(len(dirs)))
    datos = {}
    for d in dirs :
        datos[d] = {"FQ" : 0, "BAM" : 0, "ON" : 0, "OFF" : 0, "COV" : {}, "VCF" : {}, "COV_PATH" : ""}
        if ruta == "./" : # Cambiar la ruta relativa por una ruta absoluta
            path = "{}/{}".format(os.getcwd(), d)
        else :
            path = "{}/{}".format(ruta, d)
        qc = "{}/{}".format(path, cte.qcaln)
        # Guardar en el diccionario los parametros de calidad del bam
        if os.path.isfile(qc) :
            with open(qc, "r") as fi :
                aux = fi.read()
            aux2 = eval(aux)
            datos[d]["FQ"] = aux2["FASTQ"]
            datos[d]["BAM"] = aux2["BAM"]
            datos[d]["ON"] = aux2["ON"]
            datos[d]["OFF"] = aux2["OFF"]
        else :
            print("WARNING: {} no encontrado. Ejecuta AUP/bamQC.py para generarlo".format(qc))

        # Guardar en el diccionario los parametros de calidad del coverage
        cov = "{}/{}".format(path, cte.covarx)
        if os.path.isfile(cov) :
            with open(cov, "r") as fi :
                aux = fi.read()
            aux2 = eval(aux)
            datos[d]["COV"]["min"] = aux2["minimo"]
            datos[d]["COV"]["max"] = aux2["maximo"]
            datos[d]["COV"]["avg"] = aux2["media"]
            datos[d]["COV"]["med"] = aux2["mediana"]
        else :
            print("WARNING: {} no encontrado. Ejecuta AUP/coveragePanells.R para generarlo".format(cov))

        # Guardar en el diccionario el histograma con los cambios de base unica (SNVs) de cada muestra
        anno = "{}/variantCalling/raw.hg19_multianno.txt".format(path)
        kaks, fwrv, hist = vcfQC.getRatios(anno, False)
        datos[d]["VCF"] = hist

        # Guardar el path del archivo de coverage para el script de R que creara los graficos
        cov = "{}/coverage/coverageBase.txt".format(path)
        if os.path.isfile(cov) :
            datos[d]["COV_PATH"] = cov
        else :
            print("WARNING: Archivo de coverage ({}) no encontrado en la muestra {}".format(cov, d))

    return datos

def scriptR(datos) :
    filename = "globalQC.R"
    fqreads = "fq <- c("
    noms = "samps <- c("
    for d in datos.keys() :
        fqreads += "{},".format(datos[d]["FQ"])
        noms += "'{}',".format(d)

    fqreads = fqreads.rstrip(",")
    noms = noms.rstrip(",")
    fqreads += ")\n"
    noms += ")\n"


    with open(filename, "w") as fi :
        fi.write("library(RColorBrewer) # Paleta de colores para los graficos")
        fi.write("\n# Grafico de barras con la cantidad de reads de cada muestra\n")
        fi.write(fqreads)
        fi.write(noms)
        fi.write("\npng('FASTQ_distribution.png', width = 720, height = 720)\n")
        fi.write("barplot(fq, names.arg = samps, col = brewer.pal(12, 'Set3'), main = 'Numero de reads en el FASTQ')\n")
        fi.write("dev.off()\n")
        fi.write("\n# Guardar los datos de cada muestra en una variable\n")
        muestras = ""
        coverages = ""
        matriu = "mt <- matrix(c("
        vcf = ""
        matriu2 = "mt <- matrix(c("
        for k, v in datos.items() :
            sampname = k.replace("-", "").lower() # Eliminar los guiones y convertir a minusculas
            if sampname[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] : # Comprobar si el identificador de muestra es un numero. En ese caso ponerle una letra delante para que no de errores el script de R
                sampname = "p{}".format(sampname)

            muestras += "{smp} <- c({fq}, {bam}, {on}, {off})\n".format(smp = sampname, fq = v["FQ"], bam = v["BAM"], on = v["ON"], off = v["OFF"])
            coverages += "{smp}.cov <- read.table('{cov}', header = FALSE, sep = '\\t')\n".format(smp = sampname, cov = v["COV_PATH"])
            coverages += "colnames({smp}.cov) <- c('chr', 'start', 'end', 'gene', 'pos', 'coverage')\n".format(smp = sampname)
            matriu += "{},".format(sampname)
            vcf += "{smp}.snv <- c({ca}, {cg}, {ct}, {ta}, {tg}, {tc})\n".format(smp = sampname, ca = v["VCF"]["C>A"], cg = v["VCF"]["C>G"], ct = v["VCF"]["C>T"], ta = v["VCF"]["T>A"], tg = v["VCF"]["T>G"], tc = v["VCF"]["T>C"])
            matriu2 += "{}.snv,".format(sampname)

        fi.write(muestras)
        fi.write(coverages)
        fi.write(vcf)
        matriu = matriu.rstrip(",")
        matriu += "), nrow = {}, byrow = TRUE)\n".format(len(datos))
        matriu2 = matriu2.rstrip(",")
        matriu2 += "), nrow = {}, byrow = TRUE)\n".format(len(datos))
        fi.write(matriu)
        fi.write("\npng('readsQC.png', width = 720, height = 720)\n")
        fi.write("barplot(t(mt), beside=TRUE, col = brewer.pal(4, 'Set3'), names.arg = samps, main = 'Reads en FQ, alineados, on target y off target')\n")
        fi.write("dev.off()\n")

        fi.write("\n# Graficos de barras con el porcentaje de bases con un coverage determinado\n")
        for k in datos.keys() :
            sampname = k.replace("-", "").lower() # Eliminar los guiones y convertir a minusculas
            if sampname[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] : # Comprobar si el identificador de muestra es un numero. En ese caso ponerle una letra delante para que no de errores el script de R
                sampname = "p{}".format(sampname)

            fi.write("\ntotal <- length({}.cov$coverage)\n".format(sampname))
            fi.write("men0 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 0,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men30 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 30,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men100 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 100,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men500 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 500,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men1000 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 1000,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men1500 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 1500,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men2000 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 2000,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("men2500 <- round(100*length({smp}.cov[{smp}.cov$coverage >= 2500,]$coverage)/total, 2)\n".format(smp = sampname))
            fi.write("{smp}.stats <- c(men0, men30, men100, men500, men1000, men1500, men2000, men2500)\n".format(smp = sampname))
            fi.write("png('{}_coverage.png', width = 720, height = 720)\n".format(k))
            fi.write("x <- barplot({smp}.stats, main = '{nom} - % bases con _ coverage', col = brewer.pal(8, 'Set3'), ylim = c(0, 120), names.arg = c('0', '30', '100', '500', '1000', '1500', '2000', '2500'))\n".format(smp = sampname, nom = k))
            fi.write("text(x, {smp}.stats+2, as.character({smp}.stats))\n".format(smp = sampname))
            fi.write("dev.off()\n")

        fi.write("\n# Distribucion de los SNV\n")
        fi.write(matriu2)
        fi.write("\npng('snvQC.png', width = 720, height = 720)\n")
        fi.write("barplot(t(mt), beside=TRUE, col = brewer.pal(6, 'Set3'), names.arg = samps, main = 'Distribucion SNV', ylim = c(0, max(mt)+20))\n")
        fi.write("legend('topleft', fill = brewer.pal(6, 'Set3'), legend = c('C>A', 'C>G', 'C>T', 'T>A', 'T>G', 'T>C'), ncol = 3)\n")
        fi.write("dev.off()\n")

        # Buscar en la carpeta local el archivo con los genes que se han estudiado en la tanda. En caso contrario, coger la lista tipica de genes
        geneFile = os.path.basename(cte.genes)

        if not os.path.isfile(geneFile) :
            geneFile = cte.genes

        if os.path.isfile(geneFile) :
            fi.write("\n# Coverage de cada base en cada gen\n")
            with open(geneFile, "r") as fi2 :
                genes = fi2.read().strip()

            for g in genes.split("\n") :
                fi.write("\n#### {} ####\n".format(g))
                all = "maxi <- max(c("
                plot = ""
                it = 1
                for k in datos.keys() :
                    sampname = k.replace("-", "").lower() # Eliminar los guiones y convertir a minusculas
                    if sampname[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] : # Comprobar si el identificador de muestra es un numero. En ese caso ponerle una letra delante para que no de errores el script de R
                        sampname = "p{}".format(sampname)
                        
                    all += "aux{}$coverage,".format(sampname)
                    if plot == "" :
                        plot = "plot(aux{smp}$coverage, type = 'l', main = 'Coverage {gen}', col = rainbow({lon})[{it}], ylim = c(0, maxi))\n".format(smp = sampname, gen = g, lon = len(datos), it = it)
                    else :
                        plot += "lines(aux{smp}$coverage, col = rainbow({lon})[{it}])\n".format(smp = sampname, lon = len(datos), it = it)
                    it += 1
                    fi.write("aux{smp} <- {smp}.cov[{smp}.cov$gene == '{gen}',]\n".format(smp = sampname, gen = g))
                all = all.rstrip(",")
                all += "))\n"
                fi.write(all)
                fi.write("png('cov{}.png', width = 720, height = 720)\n".format(g))
                fi.write(plot)
                fi.write("legend('topright', legend = samps, fill = rainbow({lon}))\n".format(lon = len(datos)))
                fi.write("dev.off()\n")

    return filename


def main() :
    # Leer la carpeta en la que se ha invocado el programa para comprobar si se va a analizar la tanda en curso o hay que preguntar que tanda analizar
    dir = os.getcwd().split("/")[-1]
    dc = {}
    path = ""
    outDir = "informeGlobal"
    if dir.startswith(cte.prefijoTanda) :
        if os.path.isdir(outDir) :
            shutil.rmtree(outDir)
        dc = recogerDatos()
        tanda = dir.replace(cte.prefijoTanda, "")
    else :
        tanda = input("INPUT: Numero de tanda donde se realiza el control de calidad: ")
        try :
            tanda = int(tanda)
        except ValueError :
            print("ERROR: Numero de tanda erroneo")
            sys.exit(1)
        path = "{wd}/{pre}{tn}".format(wd = cte.workindir, tn = tanda, pre = cte.prefijoTanda)
        if os.path.isdir("{}/{}".format(path, outDir)) :
            shutil.rmtree("{}/{}".format(path, outDir))
        dc = recogerDatos(path)

    # Crear el script en R que creara los graficos
    arx = scriptR(dc)

    # Guardar el script de R en su lugar correspondiente. Se crea una carpeta donde se guardan todos los graficos y el script
    if path != "" :
        path = "{}/{}/".format(path, outDir)
        os.mkdir(path)
        shutil.move(arx, "{}/{}".format(path, arx))
        os.chdir(path)
    else :
        os.mkdir(outDir)
        shutil.move(arx, outDir)
        os.chdir(outDir)

    os.mkdir(imgFolder)

    # Crear los graficos en la carpetaº
    print("INFO: Ejecutando R")
    cmd = "Rscript {}".format(arx)
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0 :
        print("WARNING: El script de R no ha finalizado correctamente. Comando: {}".format(cmd))
        print(err.decode())
    else :
        print("INFO: Graficos generados correctamente")
        print("INFO: Creando web con el informe")
        # Guardar el contenido de la plantilla en una variable
        with open(cte.pathAllTemplate, "r") as fi :
            txt = fi.read()

        # PARCHE: Modificar las rutas de los graficos "fijos" snvQC.png y readsQC.png
        newImg = "{}/readsQC.png".format(imgFolder)
        pref, suf = txt.split("readsQC.png")
        txt = pref + newImg + suf
        newImg = "{}/snvQC.png".format(imgFolder)
        pref, suf = txt.split("snvQC.png")
        txt = pref + newImg + suf

        vars, bases, cov = datosPlantilla() # Recoger los datos necesarios para rellenar la plantilla

        # Mover los graficos a la carpeta de graficos
        cmd = "mv *png {}".format(imgFolder)
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0 :
            print("WARNING: No se pueden mover las imagenes creadas a la carpeta {}".format(imgFolder))
            print(err.decode())

        fic = cte.pathAllTemplate.split("/")[-1]
        with open(fic, "w") as fi :
            fi.write(txt.format(tanda = "{}{}".format(cte.prefijoTanda, tanda), variantes = vars, percentBases = cov, covBases = bases))

        shutil.copyfile(cte.pathAllCss, cte.pathAllCss.split("/")[-1])
        shutil.copyfile(cte.pathAllJs, cte.pathAllJs.split("/")[-1])
        print("INFO: Todo guardado en {}".format(os.getcwd()))


if __name__ == "__main__" :
    main()
