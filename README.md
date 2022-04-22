# Analisis aUtom&aacute;tico de Paneles
## Analizar paneles SMD autom&aacute;ticamente

Procesa las muestras de paneles secuenciadas autom&aacute;ticamente.

### Uso

```bash
$PATH_AUP/main.py
```
La interfaz tiene varios funcionalidades. La opci&oacute;n 1 crea un an&aacute;lisis t&iacute;pico del panel (crear una nueva carpeta de an&aacute;lisis, copiar los FASTQ a la carpeta de an&aacute;lisis, hacer un control de calidad de los FASTQ, alinear, recalibrar bases, hacer un variant calling germinal -usando Mutect2-, anotar las variantes usando ANNOVAR, filtrar y reanotar las variantes usando myvariant.info, guardar los resultados en un excel). Usando esta opci&oacute;n, la interfaz pedir&aacute; una ruta absoluta donde est&aacute;n los FASTQ reportados por el secuenciador. **Tip:** Para copiar la ruta absoluta de los FASTQ, se puede abrir una nueva consola, navegar a la carpeta donde est&aacute;n los FASTQ y ejecutar *pwd*. Luego copiar la salida del comando en la consola donde se est&aacute; ejecutando la interfaz.

## Otras funcionalidades

### An&aacute;lisis personalizado de las muestras

```bash
$PATH_AUP/main.py
```

Se pueden elegir los pasos del an&aacute;lisis que se quiere hacer con las muestras. Para ello, hay que elegir la opci&oacute;n 2 en la interfaz. Una vez introducida la ruta donde est&aacute;n los FASTQ, la interfaz preguntar&aacute; qu&eacute; pasos seguir para el an&aacute;lisis de las muestras. Solo  hay que ir contestando 's' o 'n' a cada una de las preguntas que hace el programa. Una vez decidido el an&aacute;lisis, el programa preguntar&aacute; por la ruta donde est&aacute;n las muestras a analizar. Autom&aacute;ticamente se crear&aacute; el log para analizar las muestras con los pasos que se han especificado.

### Analizar una &uacute;nica muestra *de novo*

```bash
$PATH_AUP/main.py
```

Funciona igual que la opci&oacute;n 2, pero para una &uacute;nica muestra. En este caso, buscar&aacute; solo en la carpeta que se ha seleccionado los FASTQ que haya en ella. No buscar&aacute; en subcarpetas. Una vez elegida la opci&oacute;n 3, la interfaz pedir&aacute; la ruta absoluta de la carpeta donde se encuentran los FASTQ que se quieren analizar. Se crear&aacute; el log del an&aacute;lisis y, posteriormente se ejecutar&aacute; dicho an&aacute;lisis.

### Control de calidad de un alineamiento en particular

El control de calidad se puede ejecutar de dos formas distintas: invocando directamente al *script* de control de calidad (bamQC.py) o usando la interfaz (main.py), opci&oacute;n 4.

#### Usando bamQC

El control de calidad se debe hacer dentro de la carpeta de la muestra. Por esto, para ejecutar este *script* se debe poner en la carpeta de la muestra. Una vez all&iacute; ejecutamos el *script*. **NOTA:** Se asume que en la carpeta de la muestra hay una subcarpeta llamada *alignment* y que el bam se llama *bwa.recal.bam*.

```bash
cd $CARPETA_DE_LA_MUESTRA_A_ANALIZAR
$PATH_AUP/bamQC.py
```

El programa crear&aacute; un archivo de texto, en formato JSON, que contiene el n&uacute;mero de *reads* que tiene el FASTQ (suma de los *reads* reportados por FASTQC), los *reads* que tiene el bam (sumatorio de las filas que tiene el bed creado), los *reads* que est&aacute;n dentro del manifest (ON target) y los que no est&aacute;n dentro del manifest (OFF target).

#### Usando la interfaz

```bash
$PATH_AUP/main.py
```

La interfaz pedir&aacute; indicar la ruta donde est&aacute; el bam en el que se quiere hacer el control de calidad. La interfaz crear&aacute; los archivos necesarios para poder hacer dicho control de calidad y reportar&aacute; la informaci&oacute;n del archivo en formato JSON en un formato m&aacute;s legible. Una vez se hayan mostrado los resultados por pantalla, la interfaz borrar&aacute; todos los archivos que ha creado.

### Crear un excel a partir de un vcf de variantes

Usando la opcion 5 de la interfaz (main.py), esta pedir&aacute; la ruta absoluta del vcf que se quiere anotar. Adem&aacute;s pedir&aacute; que se le d&eacute; un nombre identificativo a la muestra que se va a anotar. Finalmente, se pedir&aacute; el genoma de referencia que se ha usado para hacer el an&aacute;lisis previo. Las opciones disponibles del genoma de referencia son 'hg19' y 'hg38'.

### Reanalizar una muestra sin eliminar los datos hechos previamente

Usando la interfaz (main.py, opci&oacute;n 6), el programa pedir&aacute; el identificador de la muestra que se quiere reanalizar. El programa buscar&aacute; la carpeta de la tanda en la que se analiz&oacute; la muestra. Si se encuentra dicha carpeta, el programa preguntar&aacute; por el an&aacute;lisis personalizado que se quiere hacer y crear&aacute; el log con todas las instrucciones necesarias para hacer dicho an&aacute;lisis.

### Anotar un manifest

En caso de tener un manifest en el que no se sabe a qu&eacute; genes pertenece cada regi&oacute;n se puede usar la interfaz (opci&oacute;n 7) para anotar dicho manifest. El *script*, adem&aacute;, crear&aacute; el archivo gensAestudi.txt que se usa durante la fase de c&aacute;lculo de *coverage*.

#### Uso

```bash
$PATH_AUP/main.py
```

### Limpiar una tanda para archivarla

Eliminar todos los archivos no importantes generados durante el an&aacute;lisis de una tanda de paneles.

#### Uso

```bash
$PATH_AUP/cleaner.py [numero_de_tanda]
```

El programa eliminar&aacute; los archivo temporales de la tanda pasada por par&aacute;metro. Los archivos temporales son los FASTQ, los bams intermedios y los archivos anotados intermedios.

```bash
$PATH_AUP/cleaner.py
```

En caso de que no se introduzca un n&uacute;mero de tanda, el programa pedir&aacute; el n&uacute;mero de tanda que se quiere limpiar. Una vez hecho esto, ir&aacute; a la carpeta correspondiente y eliminar&aacute; los archivos FASTQ, los bams intermedios, los vcf y anotaciones intermedias.

### Crear un informe de la calidad del los FASTQ, el alineamiento y el *coverage*

El *script* crea un informe, en formato web, con todos los gr&aacute;ficos que se han generando durante el an&aacute;lisis de la muestra. En este informe, se puede consultar:
* el n&uacute;mero de *reads* secuenciados,
* el porcentaje de *reads* alineados,
* el porcentaje de *on* y *off* target,
* el coverage m&iacute;nimo, m&aacute;ximo, medio y la mediana de la muestra, así como el porcentaje de bases con un *coverage* menor de 30X, 100X, 500X y 1000X,
* el *coverage* m&iacute;nimo, m&aacute;ximo, medio y la mediana de cada uno de los genes,
* los gr&aacute;ficos de calidad de las bases, contenido de las bases, porcentaje de GC y porcentaje de duplicados, y
* los gr&aacute;ficos de cobertura general y de cada gen.

#### Uso

```bash
cd $CARPETA_DE_LA_MUESTRA_A_ANALIZAR
$PATH_AUP/infomeQC.py
```

### Crear un informe de calidad de todo el panel

El *script* crea un informe, en formato web, con los gr&aacute;ficos generos durante el an&aacute;lisis de la muestra y algunas funcionalidades extra. En este informe se puede consultar:
* una tabla con todas las variantes reportadas por todas las muestras y las veces que se ha reportado la variante en el panel
* un gr&aacute;fico con el n&uacute;mero de reads que contienen los FASTQ (FQ), los BAM y los que est&aacute;n alineados en regiones del manifest (ON target) o fuera de &eacute;l (OFF target)
* un histograma con la distribuci&oacute;n de SNV en cada muestra. Es decir, un gr&aacute;fico con el n&uacute;mero de veces que se cambia C>A, C>G, C>T, T>A, T>C y T>G en cada muestra. Los cambios complementarios se adaptan a este formato (por ejemplo, los G>T se escriben como C>A)
* un gr&aacute;fico de barras por cada muestra con el porcentaje de bases que tienen un coverage de 0 (o superior), 30 (o superior), 100 (o superior), 500 (o superior), 1000 (o superior), 1500 (o superior), 2000 (o superior) y 2500 (o superior)
* un grafico con el coverage de cada gen. El coverage de cada muestra en el gen se genera por una linea

#### Uso

```bash
cd $CARPETA_DEL_ANALISIS
$PATH_AUP/informeGlobal.py
```

### Copiar los datos finales de un panel a otra carpeta

Copia los datos necesarios para el filtrado visual a otra carpeta definida por el usuario.

#### Uso

```bash
$PATH_AUP/moverDatos.py
```

o

```bash
$PATH_AUP/moverDatos [numero de tanda] [carpeta_destino]
```

# FAQs

## &iquest;C&oacute;mo hago para modificar los programas que se ejecutan en los an&aacute;lisis?

La librer&iacute;a [constantes.py](../master/constantes.py) contiene las &oacute;rdenes para ejecutar cada uno de los programas necesarios para el an&aacute;lisis. Solo ha que modificar las constantes de esta librer&iacute;a por las rutas absolutas de ejecuci&oacute;n del programa(s) que queremos modificar.


## El manifest del panel ha cambiado. &iquest;C&oacute;mo cambio el manifest de la pipeline?

Existen dos opciones:

1. Crear el *log* de an&aacute;lisis (usando los comandos descritos al inicio de este README) y cambiar manualmente la ruta del manifest. Dicha ruta est&aacute; guardada como una constante en el *log* del an&aacute;lisis.
2. Cambiar la ruta de la constante manifest en la librer&iacute;a de [constantes](../master/constantes.py).
