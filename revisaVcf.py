#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MAIN: Comprueba si hay variantes multialelicas reportadas en un archivo vcf creado por Mutect2. Crea lineas adicionales para luego usar ANNOVAR
"""

import sys

def main(path, output = "mutect.revised.vcf") :
    """Programa principal. Abre el archivo vcf pasado por parametro y comprueba si hay variantes multialelicas. Crea un nuevo archivo (mutect.revised.vcf) con los datos obtenidos

    Comprueba si hay alguna linea en el que el genotipo sea multialelico (0/1/2, 0/1/2/3 y asi sucesivamente). En caso de encontrar alguno, crea tantas lineas adicionales
    como variantes multialelicas haya reportadas. Es decir, para el caso 0/1/2 (dos variantes en la misma posicion) creara una nueva linea en el vcf con la otra variante
    para que ANNOVAR la pueda anotar como si no fuera multialelica. En las nuevas lineas se guardaran solo los datos correspondientes a dichas variantes. La linea original
    conservara los datos de todas variantes multialelicas que se han reportado, ya que ANNOVAR los ignora cuando se convierte el vcf a formato ANNOVAR.

    Parameters
    ----------
        path : str
            Ruta donde esta el archivo vcf que se quiere revisar si contiene variantes multialelicas

    """
    header = ""
    body = ""
    with open(path, "r") as fi :
        for l in fi :
            if l.startswith("#") :
                header += l
            else :
                gt = l.split("\t")[9].split(":")[0] # Recoger, de la columna con los valores de FORMAT, el valor de la columna GT
                if len(gt.split("/")) > 2 : # La variante es multialelica
                    chr, pos, id, ref, alt, qual, filter, info, format, sample = l.split("\t")
                    newline = ""
                    for i in range(1, len(gt.split("/"))) : # Crear nuevas filas por cada variante multialelica
                        newline = "{chr}\t{pos}\t{id}\t{ref}\t".format(chr = chr, pos = pos, id = id, ref = ref)
                        newline += "{alt}\t".format(alt = alt.split(",")[i-1])
                        newline += "{qual}\t{filter}\t{info}\t{format}\t".format(qual = qual, filter = filter, info = info, format = format)
                        aux2 = format.split(":")
                        aux = sample.split(":")
                        newformat = aux[0] # Dato columna GT
                        for h in range(1, len(aux2)) :
                            if aux2[h] == "AD" or aux2[h] == "F1R2" or aux2[h] == "F2R1" :
                                cnt = "{},{}".format(aux[h].split(",")[0], aux[h].split(",")[i])
                            elif aux2[h] == "AF" :
                                cnt = aux[h].split(",")[i-1]
                            else :
                                cnt = aux[h]
                            newformat += ":{}".format(cnt)
                        newline += "{}".format(newformat)
                        body += newline
                else :
                    body += l # Agregar la fila original
    with open(output, "w") as fi :
        fi.write(header)
        fi.write(body)

if __name__ == "__main__" :
    if len(sys.argv) > 2 :
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2 :
        main(sys.argv[1])
    else :
        print("Revisar si un vcf creado por Mutect2 tiene variantes multialelicas")
        print("USO: python3 revisaVcf.py archivo.vcf [archivo_de_salida.vcf]")
