# -*- coding: utf-8 -*-
#!/usr/bin/python

import scipy.stats as stats
import sys

import getWebInfo as gw
import reAnnoFilt as anno

def main(ruta, samplename = "noName") :
    todas = anno.convertirData(ruta)
    for p in todas :
        p["population_max"], p["population_max_name"] = anno.maximMaf(p)
        p["predictor_summary"] = anno.resumPredictors(p)
        if "STRANDQ" in p.keys() :
            p["Strand_bias_score"] = p["STRANDQ"] # Mutect2 no proporciona los reads forward y los reads reverse de la variante
        else :
            p["Strand_bias_score"] = "NA"
        if "SB" in p.keys() :
            aux = p["SB"].split(",")
            refFw = int(aux[0])
            refRv = int(aux[1])
            altFw = int(aux[2])
            altRv = int(aux[3])
            odds_ratio, pvalue = stats.fisher_exact([[refFw, refRv], [altFw, altRv]])
            p["SB"] = pvalue
            p["ADF"] = "{},{}".format(refFw, altFw)
            p["ADR"] = "{},{}".format(refRv, altRv)
            if not "STRANDQ" in p.keys() :
                p["Strand_bias_score"] = refFw + altFw - refRv - altRv

        p["Ref_depth"] = p["AD"].split(",")[0]
        p["Alt_depth"] = p["AD"].split(",")[1]
        if "MMQ" in p.keys() :
            p["MQ"] = p["MMQ"] # Parche para que data2excel coja la mapping quality
        if "AF" in p.keys() :
            if p["AF"].find(",") > -1 :
                p["VAF"] = 100*float(p["AF"].split(",")[0])
            else :
                p["VAF"] = 100*float(p["AF"])
        else :
            tmp = p["AD"].split(",")
            dp = 0
            for t in tmp :
                dp += int(t)
            p["VAF"] = float(p["Alt_depth"])/dp * 100
        p["IGV_link"] = "http://localhost:60151/goto?locus=chr{}:{}".format(p["Chr"], p["Start"])
        p["sample"] = samplename

    conseq = anno.filtroConseq(todas)
    conseq = anno.addWebInfo(conseq)
    # Filtrar por MAF
    mafAlta, mafBaja = anno.filtrarMAF(conseq)
    # Filtrar por VAF
    vafAlta, vafBaja = anno.filtrarVAF(mafBaja)

    # Guardar los filtros en archivos de texto
    anno.guardarTabla(todas, "raw") # Todas las variantes recogidas en el vcf
    anno.guardarTabla(conseq, "conseq") # Variantes en regiones de splicing o exonicas (exluyendo sinonimas)
    anno.guardarTabla(mafAlta, "highMAF") # Variantes con una MAF>=0.01 en alguna columna de base de datos poblacional
    anno.guardarTabla(vafBaja, "lowVAF") # Variantes con una frecuencia alelica menor de 0.1
    anno.guardarTabla(vafAlta, "cand") # Variantes que han pasado todos los filtros anteriores

    # Mostrar por pantalla estadisticas basicas
    print("INFO: Variantes encontradas por Mutect2 {}".format(len(todas))) # Total de variantes reportadas por Strelka2
    print("INFO: Variantes conseq: {}".format(len(conseq)))
    print("INFO: MAF >= 0.1: {}".format(len(mafAlta)))
    print("INFO: MAF < 0.1: {}".format(len(mafBaja)))
    print("INFO: VAF baja: {}".format(len(vafBaja)))
    print("INFO: Variantes candidatas: {}".format(len(vafAlta)))

    # Agregar estadisticas de los tipos de variantes recogidos en el panel a la pestaña QC
    tiposVariantes = {}
    for t in todas :
        if t["Func.refGene"] == "exonic" :
            clave = "exonic_{}".format(t["ExonicFunc.refGene"])
        else :
            clave = t["Func.refGene"]
        if clave in tiposVariantes.keys() :
            tiposVariantes[clave] += 1
        else :
            tiposVariantes[clave] = 1

    with open("variants.stats.txt", "w") as fi :
        fi.write("{")
        fi.write("\'Totales\' : {},".format(len(todas)))
        fi.write("\'Conseq\' : {},".format(len(conseq)))
        fi.write("\'MAF_alta\' : {},".format(len(mafAlta)))
        fi.write("\'VAF_baja\' : {},".format(len(vafBaja)))
        fi.write("\'Candidatas\' : {}".format(len(vafAlta)))
        for k, v in tiposVariantes.items() :
            fi.write(",\'{}\' : {}".format(k, v))

        fi.write("}")


if __name__ == "__main__" :
    if len(sys.argv) > 2 :
        path = sys.argv[1]
        sample = sys.argv[2]
        main(path, sample)
    elif len(sys.argv) == 2 :
        main(path)
    else :
        print("ERROR: Numero de parametros invalido. Uso\n\tpython3 filtMutect.py archivo_multianno.txt nombreMuestra")
