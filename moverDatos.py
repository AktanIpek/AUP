#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import sys

import constantes as cte

def getTandas() :
    """
    Buscar en la carpeta donde estan los resultados de los analisis de paneles los numeros de tandas guardados para dar una ayuda al usuario

    Returns
    -------
        list
            Lista con los numeros de tandas guardados en la carpeta de analisis
    """
    tandas = []
    for root, dirs, files in os.walk(cte.workindir) :
        break
    for d in dirs :
        if d.startswith(cte.prefijoTanda) :
            aux = d.replace(cte.prefijoTanda, "")
            tandas.append(int(aux))

    return sorted(tandas)

def copiarDatos(ori, dest) :
    """
    Copia, usando rsync los bams y los excels de la carpeta origen (o) a la carpeta destino (d). Rsync crea una carpeta por cada una de las muestras encontradas

    Parameters
    ----------
        ori : str
            Carpeta origen donde buscar los bams y los excels a copiar
        dest : str
            Carpeta donde se copiaran todos los datos
    """
    muestras = [] # Lista con las carpetas de muestras encontradas
    origen = "{root}/{tanda}".format(root = cte.workindir, tanda = ori)
    bam = "alignment/{}".format(cte.finalbam)
    bai = "alignment/{}".format(cte.finalbam.replace(".bam", ".bai"))

    # Comprobar que las carpetas existen
    if not os.path.isdir(origen) :
        print("ERROR: La carpeta con la tanda ({}) no existe".format(ori))
        sys.exit(1)
    if not os.path.isdir(dest) :
        print("ERROR: Carpeta de destino ({}) no encontrada".format(dest))
        sys.exit(1)

    for root, dirs, files in os.walk(origen) :
        for d in dirs :
            # No contemplar la carpeta con el informe de calidad de la tanda
            if d != "informeGlobal" :
                muestras.append(d)
        break # Evita navegar por las subcarpetas

    print("INFO: {} muestras encontradas".format(len(muestras)))
    for m in muestras :
        current = "{}/{}".format(origen, m)
        xls = "{o}/{smp}/variantCalling/{smp}.xlsx".format(o = origen, smp = m)
        copiar = True
        # Comprobar que los archivos existen
        if not os.path.isfile("{}/{}".format(current, bam)) :
            print("WARNING: BAM no encontrado en {}/{}. La carpeta no se copiara".format(current, bam))
            copiar = False
        if not os.path.isfile("{}/{}".format(current, bai)) :
            print("WARNING: BAI no encontrado en {}/{}. La muestra no se copiara".format(current, bai))
            copiar = False
        if not os.path.isfile(xls) :
            print("WARNING: Excel no encontrado en {}. La muestra no se copiara".format(xls))
            copiar = False
        if copiar :
            print("INFO: Copiando {}".format(m))
            cmd = "rsync {o}/{smp}/{bam} {o}/{smp}/{bai} {xls} {d}/{smp}".format(o = origen, smp = m, bam = bam, bai = bai, xls = xls, d = dest)
            args = shlex.split(cmd)
            p = subprocess.Popen(args, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0 :
                print("WARNING: La copia no se produjo correctamente")
                print("\tComando usado: {}".format(cmd))
                print("\tDescripcion: {}".format(err))
    # Copiar el informe de calidad
    if os.path.isdir("{}/informeGlobal".format(origen)) :
        print("INFO: Copiando informe de calidad de la tanda")
        cmd = "rsync -a {o}/informeGlobal {d}".format(o = origen, d = dest)
        args = shlex.split(cmd)
        p = subprocess.Popen(args, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0 :
            print("WARNING: La copia no se produjo correctamente")
            print("\tComando usado: {}".format(cmd))
            print("\tDescripcion: {}".format(err))


def main(tanda = "", destino = "") :
    # Recoger carpetas de origen y destino de los datos
    if tanda == "" or destino == "" :
        disponibles = getTandas()
        tanda = input("INPUT: Numero de tanda del que se quieren copiar datos. Opciones: [{}-{}] > ".format(min(disponibles), max(disponibles)))
        destino = input("INPUT: Ruta donde se quieren guardar los datos > ")
        tanda = "tanda{}".format(tanda)
    else :
        if not tanda.startswith(cte.prefijoTanda) :
            tanda = "tanda{}".format(tanda)

    print("INFO: Copiando datos desde {root}/{tanda} a {dest}".format(root = cte.workindir, tanda = tanda, dest = destino))
    copiarDatos(tanda, destino)


if __name__ == "__main__" :
    if len(sys.argv) > 2 :
        main(sys.argv[1], sys.argv[2])
    else :
        main()
