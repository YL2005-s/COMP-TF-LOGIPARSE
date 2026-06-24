# Análisis de Teoría de la Computación — LogiParse
## Lenguajes Formales, Compiladores y Autómatas

**Autor:** Ing. Odin Delgado, Dr.  
**Cátedra:** Teoría de la Computación — Lenguajes Formales y Compiladores  
**Proyecto:** LogiParse v1.0 — Transpilador IDoc TXT → SQL Server  
**Caso de estudio:** `samples/ORD-2026-001.txt` (Alicorp S.A. → Ransa Logística)  
**Fuentes primarias:** `core/lexico.py`, `core/sintactico.py`, `core/semantico.py`,  
`core/traductor.py`, `automatas/generador.py`

---

## Índice

1. [Identificación de Lexemas](#1-identificación-de-lexemas)
2. [Identificación de Tokens](#2-identificación-de-tokens)
3. [Expresiones Regulares](#3-expresiones-regulares)
4. [Autómatas Finitos — AFND y AFD](#4-autómatas-finitos--afnd-y-afd)
5. [Gramáticas Libres de Contexto — 18 Categorías Clásicas](#5-gramáticas-libres-de-contexto--18-categorías-clásicas)
6. [Presencia de las 18 Categorías en LogiParse](#6-presencia-de-las-18-categorías-en-logiparse)
7. [Árboles Sintácticos — Caso Real](#7-árboles-sintácticos--caso-real)
8. [Conclusión](#8-conclusión)

---

## 1. Identificación de Lexemas

### 1.1 Documento de entrada

```
HDR|ORD-2026-001|20100055237|20481559927|10062026|VENTA|PEN
ITM|001|aceite-vegetal|100|KG|15.50
ITM|002|harina-preparada|50|SAC|45.00
ITM|003|leche-evaporada|200|CAJA|32.00
FTR|3|10200.00|PENDIENTE
```

El analizador léxico (`core/lexico.py`, función `analizar_lexico`) divide cada línea
por el separador `|` (`SEPARADOR = '|'`), produciendo lexemas individuales que son
luego clasificados por `clasificar_token(valor)`.

### 1.2 Tabla completa de lexemas por línea

| Línea | Pos | Lexema           | Categoría                          |
|-------|-----|------------------|------------------------------------|
| 1     | 1   | `HDR`            | Segmento de documento              |
| 1     | 2   | `ORD-2026-001`   | Código de orden                    |
| 1     | 3   | `20100055237`    | RUC emisor (11 dígitos)            |
| 1     | 4   | `20481559927`    | RUC receptor (11 dígitos)          |
| 1     | 5   | `10062026`       | Fecha DDMMYYYY                     |
| 1     | 6   | `VENTA`          | Motivo de traslado                 |
| 1     | 7   | `PEN`            | Tipo de moneda                     |
| 2     | 1   | `ITM`            | Segmento de documento              |
| 2     | 2   | `001`            | Código de ítem (3 dígitos)         |
| 2     | 3   | `aceite-vegetal` | Nombre de producto                 |
| 2     | 4   | `100`            | Cantidad (3 dígitos exactos)       |
| 2     | 5   | `KG`             | Unidad de medida                   |
| 2     | 6   | `15.50`          | Precio decimal                     |
| 3     | 1   | `ITM`            | Segmento de documento              |
| 3     | 2   | `002`            | Código de ítem                     |
| 3     | 3   | `harina-preparada`| Nombre de producto                |
| 3     | 4   | `50`             | Cantidad (2 dígitos — numérico)    |
| 3     | 5   | `SAC`            | Unidad de medida                   |
| 3     | 6   | `45.00`          | Precio decimal                     |
| 4     | 1   | `ITM`            | Segmento de documento              |
| 4     | 2   | `003`            | Código de ítem                     |
| 4     | 3   | `leche-evaporada`| Nombre de producto                 |
| 4     | 4   | `200`            | Cantidad (3 dígitos exactos)       |
| 4     | 5   | `CAJA`           | Unidad de medida                   |
| 4     | 6   | `32.00`          | Precio decimal                     |
| 5     | 1   | `FTR`            | Segmento de documento              |
| 5     | 2   | `3`              | Total ítems (1 dígito — numérico)  |
| 5     | 3   | `10200.00`       | Monto total decimal                |
| 5     | 4   | `PENDIENTE`      | Estado de la orden                 |

**Total de lexemas:** 29  
**Total de líneas:** 5 (1 HDR + 3 ITM + 1 FTR)

### 1.3 Clasificación por categoría semántica

| Categoría              | Lexemas encontrados                                         |
|------------------------|-------------------------------------------------------------|
| Segmentos              | HDR, ITM (×3), FTR                                         |
| Identificadores        | ORD-2026-001                                               |
| Registros numéricos    | 20100055237, 20481559927, 10062026                         |
| Nombres de producto    | aceite-vegetal, harina-preparada, leche-evaporada          |
| Cantidades             | 100, 50, 200                                               |
| Códigos de ítem        | 001, 002, 003                                              |
| Unidades de medida     | KG, SAC, CAJA                                              |
| Precios unitarios      | 15.50, 45.00, 32.00                                        |
| Palabras clave         | VENTA, PEN, PENDIENTE                                      |
| Totalizadores FTR      | 3, 10200.00                                                |

> **Nota sobre ambigüedad:** Los valores `100` y `200` (3 dígitos) son clasificados
> como `mis_codigos_item` porque ese token aparece *antes* que `mis_variables_numericas`
> en la lista TOKENS de `lexico.py`. El orden de prioridad es determinístico: gana el
> primer patrón que hace match. Esto es equivalente al comportamiento de Flex con reglas
> ordenadas.

---

## 2. Identificación de Tokens

### 2.1 Definición formal

Un **token** es el par (categoría, lexema) producido por el analizador léxico. En
`core/lexico.py` se definen 13 tokens en la lista `TOKENS`, procesados en orden
estricto por `clasificar_token()`. El primer patrón que hace match gana.

### 2.2 Tabla de tokens del sistema LogiParse

| #  | Token                     | Descripción                                          | Ejemplo real              |
|----|---------------------------|------------------------------------------------------|---------------------------|
| 1  | `mis_segmentos_doc`       | Identificador del tipo de segmento IDoc              | `HDR`, `ITM`, `FTR`       |
| 2  | `mis_codigos_orden`       | Código de orden PREFIJO-AÑO-SECUENCIA               | `ORD-2026-001`            |
| 3  | `mis_variables_ruc`       | RUC peruano de exactamente 11 dígitos               | `20100055237`             |
| 4  | `mis_variables_fecha`     | Fecha DDMMYYYY sin separadores (8 dígitos)          | `10062026`                |
| 5  | `mis_motivos_traslado`    | Motivo del traslado comercial                        | `VENTA`, `COMPRA`         |
| 6  | `mis_tipos_moneda`        | Moneda de la transacción                            | `PEN`, `USD`              |
| 7  | `mis_codigos_item`        | Número de ítem con padding de ceros (3 dígitos)     | `001`, `002`, `003`       |
| 8  | `mis_nombres_producto`    | Nombre compuesto en minúsculas con guión            | `aceite-vegetal`          |
| 9  | `mis_unidades_medida`     | Unidad de medida logística                          | `KG`, `SAC`, `CAJA`       |
| 10 | `mis_estados_orden`       | Estado de procesamiento de la orden                 | `PENDIENTE`, `PROCESADO`  |
| 11 | `mis_variables_decimales` | Número decimal con exactamente 2 decimales          | `15.50`, `10200.00`       |
| 12 | `mis_variables_numericas` | Entero positivo sin restricción de longitud         | `50`, `3`                 |
| 13 | `mis_variables_texto`     | Cadena alfanumérica libre (comodín)                 | `texto-libre.123`         |

> El token `DESCONOCIDO` es retornado por `clasificar_token()` cuando ningún patrón
> hace match, generando un error léxico registrado en `errores`.

### 2.3 Tabla completa de clasificación para ORD-2026-001.txt

| Lexema             | Token                     | Patrón que matchea             |
|--------------------|---------------------------|--------------------------------|
| `HDR`              | `mis_segmentos_doc`       | `^(HDR\|ITM\|FTR)$`            |
| `ORD-2026-001`     | `mis_codigos_orden`       | `^[A-Z]+-\d{4}-\d{3}$`        |
| `20100055237`      | `mis_variables_ruc`       | `^\d{11}$`                    |
| `20481559927`      | `mis_variables_ruc`       | `^\d{11}$`                    |
| `10062026`         | `mis_variables_fecha`     | `^\d{8}$`                     |
| `VENTA`            | `mis_motivos_traslado`    | `^(VENTA\|COMPRA\|DEVOLUCION)$`|
| `PEN`              | `mis_tipos_moneda`        | `^(PEN\|USD)$`                |
| `ITM` (×3)         | `mis_segmentos_doc`       | `^(HDR\|ITM\|FTR)$`           |
| `001`, `002`, `003`| `mis_codigos_item`        | `^\d{3}$`                     |
| `aceite-vegetal`   | `mis_nombres_producto`    | `^[a-z]+-[a-z]+$`             |
| `harina-preparada` | `mis_nombres_producto`    | `^[a-z]+-[a-z]+$`             |
| `leche-evaporada`  | `mis_nombres_producto`    | `^[a-z]+-[a-z]+$`             |
| `100`              | `mis_codigos_item`        | `^\d{3}$` ← gana por prioridad|
| `50`               | `mis_variables_numericas` | `^\d+$` ← 2 dígitos, no es \d{3}|
| `200`              | `mis_codigos_item`        | `^\d{3}$` ← gana por prioridad|
| `KG`               | `mis_unidades_medida`     | `^(KG\|SAC\|CAJA\|UNID)$`    |
| `SAC`              | `mis_unidades_medida`     | `^(KG\|SAC\|CAJA\|UNID)$`    |
| `CAJA`             | `mis_unidades_medida`     | `^(KG\|SAC\|CAJA\|UNID)$`    |
| `15.50`, `45.00`, `32.00`| `mis_variables_decimales`| `^\d+\.\d{2}$`         |
| `FTR`              | `mis_segmentos_doc`       | `^(HDR\|ITM\|FTR)$`           |
| `3`                | `mis_variables_numericas` | `^\d+$`                       |
| `10200.00`         | `mis_variables_decimales` | `^\d+\.\d{2}$`                |
| `PENDIENTE`        | `mis_estados_orden`       | `^(PENDIENTE\|PROCESADO\|ANULADO)$`|

---

## 3. Expresiones Regulares

### 3.1 Fundamento teórico

Una **expresión regular** (ER) define un **lenguaje regular** — el conjunto (posiblemente
infinito) de cadenas que el patrón acepta. Todo lenguaje regular es reconocible por un
Autómata Finito (AFND o AFD) y viceversa (Teorema de Kleene, 1956).

Notación formal: `L(r)` denota el lenguaje descrito por la expresión regular `r`.

### 3.2 Las 13 expresiones regulares de `core/lexico.py`

#### ER-1: `mis_segmentos_doc` — `^(HDR|ITM|FTR)$`

```
L = { HDR, ITM, FTR }     (conjunto finito — 3 palabras)
```

Reconoce exactamente las tres palabras clave del protocolo IDoc.
Los anclajes `^` y `$` garantizan match completo de la cadena.
El operador `|` es la unión de lenguajes regulares.

#### ER-2: `mis_codigos_orden` — `^[A-Z]+-\d{4}-\d{3}$`

```
L = { s-aaaa-nnn | s ∈ [A-Z]+,  a ∈ [0-9],  n ∈ [0-9] }
    Longitud mínima: 1+1+4+1+3 = 10 caracteres
```

`[A-Z]+` — uno o más caracteres alfabéticos mayúsculos (prefijo de empresa).
`\d{4}` — exactamente 4 dígitos (año).
`\d{3}` — exactamente 3 dígitos (secuencia).
Los guiones `-` son literales delimitadores.

#### ER-3: `mis_variables_ruc` — `^\d{11}$`

```
L = { w ∈ {0-9}* | |w| = 11 }     (lenguaje de cardinalidad 10^11)
```

Reconoce exactamente cadenas de 11 dígitos decimales. Modela el
Registro Único de Contribuyente (RUC) peruano. La restricción semántica
adicional (verificación de dígito verificador) se aplica en `semantico.py`.

#### ER-4: `mis_variables_fecha` — `^\d{8}$`

```
L = { w ∈ {0-9}* | |w| = 8 }     → formato DDMMYYYY implícito
```

La ER acepta cualquier cadena de 8 dígitos. La validación semántica
(`datetime.strptime(fecha_raw, '%d%m%Y')` en `semantico.py` línea 59)
garantiza que sea una fecha real. La ER es un filtro léxico, no un
validador semántico.

#### ER-5: `mis_motivos_traslado` — `^(VENTA|COMPRA|DEVOLUCION)$`

```
L = { VENTA, COMPRA, DEVOLUCION }     (conjunto finito — 3 palabras)
```

Enumeración cerrada de los motivos de traslado permitidos por SUNAT
para guías de remisión peruanas.

#### ER-6: `mis_tipos_moneda` — `^(PEN|USD)$`

```
L = { PEN, USD }     (conjunto finito — 2 palabras)
```

Códigos ISO 4217 de moneda aceptados por el sistema.

#### ER-7: `mis_codigos_item` — `^\d{3}$`

```
L = { w ∈ {0-9}* | |w| = 3 }     → { 000, 001, ..., 999 }
```

Exactamente 3 dígitos con padding de ceros (ej. `001`, `099`).

#### ER-8: `mis_nombres_producto` — `^[a-z]+-[a-z]+$`

```
L = { a-b | a ∈ [a-z]+,  b ∈ [a-z]+ }
```

Nombre compuesto de dos palabras en minúsculas separadas por un guión.
No permite dígitos, mayúsculas ni múltiples guiones.

#### ER-9: `mis_unidades_medida` — `^(KG|SAC|CAJA|UNID)$`

```
L = { KG, SAC, CAJA, UNID }     (conjunto finito — 4 palabras)
```

Vocabulario cerrado de unidades de medida del dominio logístico.

#### ER-10: `mis_estados_orden` — `^(PENDIENTE|PROCESADO|ANULADO)$`

```
L = { PENDIENTE, PROCESADO, ANULADO }     (conjunto finito — 3 palabras)
```

Estados del ciclo de vida de una orden de despacho.

#### ER-11: `mis_variables_decimales` — `^\d+\.\d{2}$`

```
L = { w.dd | w ∈ {0-9}+,  d ∈ {0-9} }
    Ejemplos: 0.00, 15.50, 10200.00
```

Número decimal con exactamente **dos** cifras decimales. El punto `.`
es un literal (no el metacaracter de ER). `\d+` acepta enteros de
cualquier longitud, `\d{2}` fuerza exactamente dos decimales.

#### ER-12: `mis_variables_numericas` — `^\d+$`

```
L = { w ∈ {0-9}+ }     (todos los enteros positivos en decimal)
```

Uno o más dígitos sin punto decimal. Actúa como **comodín numérico**
de baja prioridad — si ningún token más específico (RUC 11 dígitos,
fecha 8 dígitos, código ítem 3 dígitos) hace match primero, este captura
cualquier entero.

#### ER-13: `mis_variables_texto` — `^[A-Za-z0-9\-\.]+$`

```
L = { w ∈ (A-Za-z0-9\-\.)+ }
```

Comodín alfanumérico de última instancia. Acepta letras, dígitos,
guiones y puntos. Diseñado para capturar valores no categorizados por
los tokens anteriores, actuando como el token `default` de Flex.

### 3.3 Jerarquía de especificidad (orden de prioridad)

```
más específico ─────────────────────────────────────────── menos específico
      ↓
mis_segmentos_doc       (conjunto finito de 3)
mis_codigos_orden       (estructura PREF-AAAA-NNN)
mis_variables_ruc       (exactamente 11 dígitos)
mis_variables_fecha     (exactamente 8 dígitos)
mis_motivos_traslado    (conjunto finito de 3)
mis_tipos_moneda        (conjunto finito de 2)
mis_codigos_item        (exactamente 3 dígitos)
mis_nombres_producto    (a-z + guión + a-z)
mis_unidades_medida     (conjunto finito de 4)
mis_estados_orden       (conjunto finito de 3)
mis_variables_decimales (d+.d{2})
mis_variables_numericas (d+)                ← comodín numérico
mis_variables_texto     (alfanum libre)     ← comodín general
      ↑
más general
```

---

## 4. Autómatas Finitos — AFND y AFD

### 4.1 Definición formal

Un **Autómata Finito No Determinista (AFND)** se define como la 5-tupla:

```
M = (Q, Σ, δ, q₀, F)

donde:
  Q   = conjunto finito de estados
  Σ   = alfabeto de entrada
  δ   = Q × (Σ ∪ {ε}) → 2^Q   (función de transición no determinista)
  q₀  = estado inicial  (q₀ ∈ Q)
  F   = conjunto de estados de aceptación  (F ⊆ Q)
```

Un **AFD** es el caso particular donde `δ: Q × Σ → Q` (función total determinista,
sin transiciones ε).

### 4.2 AFND Global del sistema (de `automatas/generador.py`)

```
Q    = {q0, q1, q2, q3, q4, q5, qE}
Σ    = {#, H, I, F, [0-9], [a-z], [A-Z], '.', '-', otro}
q₀   = q0
F    = {q1, q2, q3, q4, q5}
```

**Descripción:** `"AFND para reconocimiento de tokens del formato IDoc logístico"`

#### Función de transición δ (AFND global):

| Desde | Con         | Hacia | Descripción                         |
|-------|-------------|-------|-------------------------------------|
| `q0`  | `#`         | `q1`  | Inicio de segmento                  |
| `q1`  | `H,I,F`     | `q1`  | Primera letra del segmento          |
| `q1`  | `D,T,R`     | `q1`  | Segunda letra del segmento          |
| `q1`  | `ε`         | `q2`  | HDR reconocido (transición vacía)   |
| `q1`  | `ε`         | `q3`  | ITM reconocido (transición vacía)   |
| `q1`  | `ε`         | `q4`  | FTR reconocido (transición vacía)   |
| `q0`  | `[0-9]`     | `q5`  | Inicio de número/RUC/fecha          |
| `q5`  | `[0-9]`     | `q5`  | Dígitos consecutivos (loop)         |
| `q0`  | `[a-z]`     | `q2`  | Inicio de producto/texto            |
| `q2`  | `[a-z\-]`   | `q2`  | Caracteres de producto (loop)       |
| `q0`  | `otro`      | `qE`  | Token no reconocido                 |

**El no-determinismo** reside en las tres transiciones ε desde `q1` hacia `q2`, `q3`
y `q4`: tras leer las letras del segmento, el autómata puede estar
simultáneamente en múltiples estados — rasgo que el AFD eliminará mediante
construcción de subconjuntos.

#### Diagrama ASCII — AFND Global:

```
                  ε → q2 (HDR)
                  ε → q3 (ITM)
   #    H,I,F,D,T,R  ε → q4 (FTR)
q0 ──→ q1 ──────────→ {q2,q3,q4}*

q0 ──[0-9]──→ q5 ──[0-9]──→ q5  (loop)
q0 ──[a-z]──→ q2 ──[a-z,-]──→ q2 (loop)
q0 ──otro───→ qE

* Estados de aceptación: q1, q2, q3, q4, q5
```

### 4.3 AFD Global equivalente (de `automatas/generador.py`)

```
Q    = {q0, q1, q2, q3, q4, q5, q6, qE}
Σ    = {#, H, I, F, [0-9], [a-z], '.', otro}
q₀   = q0
F    = {q2, q3, q4, q5, q6}
```

**Descripción:** `"AFD determinista equivalente para el reconocimiento de tokens logísticos"`

#### Función de transición δ (AFD global):

| Desde | Con       | Hacia | Descripción                          |
|-------|-----------|-------|--------------------------------------|
| `q0`  | `#`       | `q1`  | Inicio segmento doc                  |
| `q1`  | `H`       | `q2`  | HDR → encabezado (acepta)            |
| `q1`  | `I`       | `q3`  | ITM → ítem (acepta)                  |
| `q1`  | `F`       | `q4`  | FTR → pie (acepta)                   |
| `q0`  | `[0-9]`   | `q5`  | Inicio numérico                      |
| `q5`  | `[0-9]`   | `q5`  | Dígitos continuos (loop)             |
| `q5`  | `.`       | `q6`  | Inicio parte decimal                 |
| `q6`  | `[0-9]`   | `q6`  | Decimales (loop)                     |
| `q0`  | `[a-z]`   | `q5`  | Inicio texto/producto                |
| `q0`  | `otro`    | `qE`  | Error                                |
| `qE`  | `cualq.`  | `qE`  | Estado trampa (absorbe errores)      |

#### Diagrama ASCII — AFD Global:

```
       #          H ──→ q2* (HDR)
q0 ──────→ q1 ── I ──→ q3* (ITM)
                  F ──→ q4* (FTR)

q0 ──[0-9]──→ q5* ──[0-9]──→ q5* (loop enteros)
                  └──'.────→ q6* ──[0-9]──→ q6* (loop decimales)

q0 ──[a-z]──→ q5*
q0 ──otro───→ qE  ──cualquiera──→ qE (trampa)

* Estados de aceptación: q2, q3, q4, q5, q6
```

### 4.4 Tabla de transiciones del AFD Global

Definida en `automatas/generador.py` → `generar_automatas()` → `tabla`:

| Estado | `#`  | `H`  | `I`  | `F`  | `[0-9]` | `[a-z]` | `.`  | `otro` |
|--------|------|------|------|------|---------|---------|------|--------|
| `q0`   | `q1` | `qE` | `qE` | `qE` | `q5`    | `q5`    | `qE` | `qE`   |
| `q1`   | `qE` | `q2` | `q3` | `q4` | `qE`    | `qE`    | `qE` | `qE`   |
| `q2`*  | `qE` | `qE` | `qE` | `qE` | `qE`    | `qE`    | `qE` | `qE`   |
| `q3`*  | `qE` | `qE` | `qE` | `qE` | `qE`    | `qE`    | `qE` | `qE`   |
| `q4`*  | `qE` | `qE` | `qE` | `qE` | `qE`    | `qE`    | `qE` | `qE`   |
| `q5`*  | `qE` | `qE` | `qE` | `qE` | `q5`    | `q5`    | `q6` | `qE`   |
| `q6`*  | `qE` | `qE` | `qE` | `qE` | `q6`    | `qE`    | `qE` | `qE`   |
| `qE`   | `qE` | `qE` | `qE` | `qE` | `qE`    | `qE`    | `qE` | `qE`   |

`*` = estado de aceptación

### 4.5 Autómatas individuales por token

Los autómatas específicos están definidos en `automatas/generador.py` →
`AUTOMATAS_POR_TOKEN`. A continuación se documentan los más relevantes.

---

#### Token `mis_segmentos_doc` — `^(HDR|ITM|FTR)$`

**AFND** (11 estados + q0, sin transiciones ε directas a qH0/qI0/qF0):

```
Q = {q0, qH0,qH1,qH2,qH3, qI0,qI1,qI2,qI3, qF0,qF1,qF2,qF3}
F = {qH3, qI3, qF3}
```

```
         ε          H      D      R
q0 ─────────→ qH0 ──→ qH1 ──→ qH2 ──→ qH3*

         ε          I      T      M
q0 ─────────→ qI0 ──→ qI1 ──→ qI2 ──→ qI3*

         ε          F      T      R
q0 ─────────→ qF0 ──→ qF1 ──→ qF2 ──→ qF3*
```

**AFD** (construcción de subconjuntos — 11 estados + qE):

| Estado | `H`  | `D`  | `R`  | `I`  | `T`  | `M`  | `F`  | `otro` |
|--------|------|------|------|------|------|------|------|--------|
| `q0`   | `q1` | `qE` | `qE` | `q4` | `qE` | `qE` | `q7` | `qE`   |
| `q1`   | `qE` | `q2` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `q2`   | `qE` | `qE` | `q3` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `q3`*  | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `q4`   | `qE` | `qE` | `qE` | `qE` | `q5` | `qE` | `qE` | `qE`   |
| `q5`   | `qE` | `qE` | `qE` | `qE` | `qE` | `q6` | `qE` | `qE`   |
| `q6`*  | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `q7`   | `qE` | `qE` | `qE` | `qE` | `q8` | `qE` | `qE` | `qE`   |
| `q8`   | `qE` | `qE` | `q9` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `q9`*  | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE`   |
| `qE`   | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE` | `qE`   |

---

#### Token `mis_codigos_orden` — `^[A-Z]+-\d{4}-\d{3}$`

**AFND** (11 estados, lineal con un loop en q1):

```
Q = {q0, q1, ..., q10},   F = {q10}

q0 ──[A-Z]──→ q1 ──[A-Z]──→ q1  (loop letras mayúsculas)
q1 ──'-'────→ q2 ──[0-9]──→ q3 ──[0-9]──→ q4 ──[0-9]──→ q5 ──[0-9]──→ q6
q6 ──'-'────→ q7 ──[0-9]──→ q8 ──[0-9]──→ q9 ──[0-9]──→ q10*
```

**Tabla de transiciones AFD:**

| Estado  | `[A-Z]` | `-`  | `[0-9]` | `otro` |
|---------|---------|------|---------|--------|
| `q0`    | `q1`    | `qE` | `qE`    | `qE`   |
| `q1`    | `q1`    | `q2` | `qE`    | `qE`   |
| `q2`    | `qE`    | `qE` | `q3`    | `qE`   |
| `q3`    | `qE`    | `qE` | `q4`    | `qE`   |
| `q4`    | `qE`    | `qE` | `q5`    | `qE`   |
| `q5`    | `qE`    | `qE` | `q6`    | `qE`   |
| `q6`    | `qE`    | `q7` | `qE`    | `qE`   |
| `q7`    | `qE`    | `qE` | `q8`    | `qE`   |
| `q8`    | `qE`    | `qE` | `q9`    | `qE`   |
| `q9`    | `qE`    | `qE` | `q10`   | `qE`   |
| `q10`*  | `qE`    | `qE` | `qE`    | `qE`   |
| `qE`    | `qE`    | `qE` | `qE`    | `qE`   |

---

#### Token `mis_variables_ruc` — `^\d{11}$`

**AFND / AFD** (12 estados, cadena lineal de 11 dígitos):

```
q0 ──[0-9]──→ q1 ──[0-9]──→ q2 ──...──→ q10 ──[0-9]──→ q11*
```

Tabla resumida (todos los arcos etiquetados `[0-9]`, cualquier otro → `qE`):

| q0→q1 | q1→q2 | q2→q3 | q3→q4 | q4→q5 | q5→q6 | q6→q7 | q7→q8 | q8→q9 | q9→q10 | q10→q11* |

---

#### Token `mis_variables_fecha` — `^\d{8}$`

**AFD** (9 estados, cadena lineal de 8 dígitos):

```
q0 ──[0-9]──→ q1(DD₁) ──[0-9]──→ q2(DD₂) ──[0-9]──→ q3(MM₁) ──[0-9]──→ q4(MM₂)
              ──[0-9]──→ q5(YY₁) ──[0-9]──→ q6(YY₂) ──[0-9]──→ q7(YY₃) ──[0-9]──→ q8*
```

---

#### Token `mis_nombres_producto` — `^[a-z]+-[a-z]+$`

**AFD** (5 estados con loops):

```
q0 ──[a-z]──→ q1 ──[a-z]──→ q1  (loop primera palabra)
q1 ──'-'────→ q2 ──[a-z]──→ q3* ──[a-z]──→ q3*  (loop segunda palabra)
```

**Tabla de transiciones:**

| Estado | `[a-z]` | `-`  | `otro` |
|--------|---------|------|--------|
| `q0`   | `q1`    | `qE` | `qE`   |
| `q1`   | `q1`    | `q2` | `qE`   |
| `q2`   | `q3`    | `qE` | `qE`   |
| `q3`*  | `q3`    | `qE` | `qE`   |
| `qE`   | `qE`    | `qE` | `qE`   |

---

#### Token `mis_variables_decimales` — `^\d+\.\d{2}$`

**AFD** (6 estados):

```
q0 ──[0-9]──→ q1 ──[0-9]──→ q1  (loop parte entera)
q1 ──'.'────→ q2 ──[0-9]──→ q3 ──[0-9]──→ q4*
```

**Tabla de transiciones:**

| Estado | `[0-9]` | `.`  | `otro` |
|--------|---------|------|--------|
| `q0`   | `q1`    | `qE` | `qE`   |
| `q1`   | `q1`    | `q2` | `qE`   |
| `q2`   | `q3`    | `qE` | `qE`   |
| `q3`   | `q4`    | `qE` | `qE`   |
| `q4`*  | `qE`    | `qE` | `qE`   |
| `qE`   | `qE`    | `qE` | `qE`   |

---

#### Token `mis_variables_numericas` — `^\d+$`

**AFD** (3 estados — el más simple):

```
q0 ──[0-9]──→ q1* ──[0-9]──→ q1*  (loop, acepta desde el primer dígito)
q0 ──otro───→ qE
```

---

### 4.6 Máquina de Turing del transpilador (de `automatas/generador.py`)

La MT modela el proceso completo TXT → SQL en 10 estados.

```
M_T = (Q, Γ, Σ, δ, q0, qACEPT, qREJECT)

Q       = {q0,q1,q2,q3,q4,q5,q6,q7,qACEPT,qREJECT}
Γ       = {H,D,R,I,T,M,F,|,0-9,a-z,-,.,□,✓,✗,SQL}
Σ       = Γ \ {□,✓,✗,SQL}    (símbolos de entrada)
q0      = estado inicial
qACEPT  = estado de aceptación (SQL generado)
qREJECT = estado de rechazo (error léxico)
```

#### Función de transición δ(q, a) = (q', b, D):

| Estado  | Lee       | Escribe | Mueve | Hacia      | Semántica                          |
|---------|-----------|---------|-------|------------|------------------------------------|
| `q0`    | `H/I/F`   | `✓`     | R     | `q1`       | Lee tipo de segmento HDR/ITM/FTR   |
| `q0`    | `otro`    | `✗`     | R     | `qREJECT`  | Token no reconocido — error léxico |
| `q1`    | `\|`      | `✓`     | R     | `q2`       | Lee separador de campo             |
| `q2`    | `0-9/a-z` | `✓`     | R     | `q3`       | Lee valor del campo (token)        |
| `q3`    | `0-9/a-z/-`| `✓`   | R     | `q3`       | Continúa leyendo valor             |
| `q3`    | `\|`      | `✓`     | R     | `q2`       | Siguiente campo de la línea        |
| `q3`    | `□`       | `□`     | R     | `q4`       | Fin de línea — valida semántica    |
| `q4`    | `H/I/F`   | `✓`     | R     | `q1`       | Siguiente línea del documento      |
| `q4`    | `□`       | `□`     | R     | `q5`       | Fin del documento — inicia trad.   |
| `q5`    | `✓`       | `SQL`   | R     | `q6`       | Genera INSERT INTO ordenes         |
| `q6`    | `✓`       | `SQL`   | R     | `q7`       | Genera INSERT INTO detalle_orden   |
| `q7`    | `□`       | `□`     | R     | `qACEPT`   | SQL generado — traducción completa |

**Cinta de ejemplo** (cabezal inicial en posición 0):

```
┌─┬─┬─┬─┬─────────────┬─────────────┬─┐
│H│D│R│|│ORD-2026-001│20100055237 │...│□│
└─┴─┴─┴─┴─────────────┴─────────────┴─┘
 ▲
 q0
```

---

## 5. Gramáticas Libres de Contexto — 18 Categorías Clásicas

### 5.1 Definición formal de una GLC

Una **Gramática Libre de Contexto (GLC)** es una 4-tupla:

```
G = (N, Σ, P, S)

donde:
  N   = conjunto finito de símbolos NO TERMINALES (variables)
  Σ   = conjunto finito de símbolos TERMINALES (alfabeto del lenguaje)
  P   = conjunto finito de PRODUCCIONES de la forma: A → α
           siendo A ∈ N  y  α ∈ (N ∪ Σ)*
  S   = símbolo inicial (S ∈ N)
```

**Componentes:**

| Componente | Notación | Descripción |
|------------|----------|-------------|
| No terminal | `A, B, C` en mayúscula | Variable que puede ser reemplazada |
| Terminal   | `a, b, c` en minúscula | Símbolo del lenguaje final |
| Producción | `A → α`  | Regla de reescritura de A |
| Derivación | `α ⇒ β`  | Un paso de aplicación de una producción |
| Lenguaje   | `L(G)` = `{w ∈ Σ* \| S ⇒* w}` | Todas las cadenas derivables desde S |

**"Libre de contexto"** significa que las producciones tienen exactamente un no terminal
en el lado izquierdo — no dependen del contexto en que aparecen.

### 5.2 Las 18 categorías clásicas con sus GLC

---

#### CAT-1: Números enteros

```
G_NUM = ({NUM, D}, {0,1,...,9}, P, NUM)

P:
  NUM → D
  NUM → NUM D
  D   → 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

**Lenguaje:** `L = { w ∈ {0-9}+ }` — todos los enteros positivos en decimal.

---

#### CAT-2: Identificadores

```
G_ID = ({ID, L, R, C}, {a-z, A-Z, 0-9, _}, P, ID)

P:
  ID → L
  ID → L R
  R  → C
  R  → R C
  L  → a | b | ... | z | A | B | ... | Z | _
  C  → L | 0 | 1 | ... | 9
```

**Lenguaje:** `L = { w | w comienza con letra/_, resto alfanumérico }`.

---

#### CAT-3: Expresiones aritméticas

```
G_ARITH = ({E, T, F}, {+, -, *, /, (, ), id, num}, P, E)

P:
  E → E + T | E - T | T
  T → T * F | T / F | F
  F → ( E ) | id | num
```

**Lenguaje:** expresiones con operadores binarios, paréntesis, identificadores y números.
Esta gramática es ambigua en la versión simple; la versión estratificada E/T/F
codifica la precedencia (*/ antes que +-) y la asociatividad izquierda.

---

#### CAT-4: Expresiones relacionales

```
G_REL = ({R, E, Op}, {<, >, <=, >=, ==, !=}, P, R)

P:
  R  → E Op E
  Op → < | > | <= | >= | == | !=
  E  → (expresión aritmética, ver CAT-3)
```

**Lenguaje:** comparaciones entre dos expresiones, resultado booleano.

---

#### CAT-5: Expresiones lógicas

```
G_LOG = ({L, C}, {&&, ||, !, true, false}, P, L)

P:
  L → L && C | L || C | C
  C → ! C | ( L ) | true | false | (expresión relacional CAT-4)
```

**Lenguaje:** expresiones booleanas compuestas con conectivos lógicos.

---

#### CAT-6: Asignaciones

```
G_ASIG = ({ASIG, ID, E}, {:=, =}, P, ASIG)

P:
  ASIG → ID := E
  ASIG → ID =  E
  ID   → (ver CAT-2)
  E    → (expresión aritmética, ver CAT-3)
```

**Lenguaje:** instrucciones de asignación de valor a variable.

---

#### CAT-7: Sentencia IF (simple)

```
G_IF = ({S, COND, BLOQUE}, {if, then}, P, S)

P:
  S      → if COND then BLOQUE
  COND   → (expresión lógica, ver CAT-5)
  BLOQUE → (lista de sentencias, ver CAT-11)
```

---

#### CAT-8: Sentencia IF-ELSE

```
G_IFELSE = ({S, COND, B₁, B₂}, {if, then, else}, P, S)

P:
  S  → if COND then B₁ else B₂
  S  → if COND then B₁
```

**Ambigüedad del dangling else:** la producción anterior es ambigua. Se resuelve con:

```
  S_match   → if COND then S_match else S_match | otros
  S_unmatch → if COND then S | if COND then S_match else S_unmatch
```

---

#### CAT-9: Ciclo WHILE

```
G_WHILE = ({S, COND, B}, {while, do}, P, S)

P:
  S    → while COND do B
  COND → (expresión lógica)
  B    → (lista de sentencias)
```

**Lenguaje:** potencialmente infinito (ciclo no acotado) — requiere análisis semántico
para detectar terminación.

---

#### CAT-10: Ciclo FOR

```
G_FOR = ({S, INIT, COND, STEP, B}, {for, to, step, do}, P, S)

P:
  S    → for INIT to COND step STEP do B
  S    → for INIT to COND do B          (paso implícito = 1)
  INIT → ID := E
```

---

#### CAT-11: Lista de sentencias

```
G_LIST = ({LIST, S}, {;}, P, LIST)

P:
  LIST → S
  LIST → LIST ; S
  S    → (cualquier sentencia)
```

**Lenguaje:** secuencias de sentencias separadas por punto y coma.

---

#### CAT-12: Declaraciones de variables

```
G_DECL = ({DECL, TYPE, VARLIST, ID}, {int, float, string, ,, ;}, P, DECL)

P:
  DECL    → TYPE VARLIST ;
  VARLIST → ID
  VARLIST → VARLIST , ID
  TYPE    → int | float | string | bool | ...
```

---

#### CAT-13: Funciones (definición)

```
G_FUNC = ({FUNC, NAME, PARAMS, BODY, TYPE}, {function, def, return, (, ), {}}, P, FUNC)

P:
  FUNC   → TYPE Name ( PARAMS ) { BODY }
  PARAMS → ε | PARAMLIST
  BODY   → LIST return E ;
```

---

#### CAT-14: Parámetros formales

```
G_PARAM = ({PARAMLIST, PARAM, TYPE, ID}, {,}, P, PARAMLIST)

P:
  PARAMLIST → PARAM
  PARAMLIST → PARAMLIST , PARAM
  PARAM     → TYPE ID
```

---

#### CAT-15: Llamadas a funciones

```
G_CALL = ({CALL, NAME, ARGS}, {(, ), ,}, P, CALL)

P:
  CALL → NAME ( ARGS )
  ARGS → ε | ARGLIST
  ARGLIST → E
  ARGLIST → ARGLIST , E
```

---

#### CAT-16: Cadenas balanceadas

```
G_BAL = ({S}, {a, b}, P, S)    -- donde 'a' abre y 'b' cierra

P:
  S → ε | a S b S
```

**Lenguaje:** `L = { ww^R equivalente | número de 'a' = número de 'b', balanceadas }`
Este lenguaje NO es regular — requiere memoria (pila) → solo reconocible por
Autómata de Pila (PDA). Ejemplo prototípico de lenguaje CFL no regular.

---

#### CAT-17: Paréntesis balanceados

```
G_PAREN = ({P}, {(, )}, P, P)

P:
  P → ε | ( P ) | P P
```

**Lenguaje:** `L = { w | cada '(' tiene su ')' correspondiente }`.
Variante de CAT-16 con el mismo alfabeto `{(,)}`.

---

#### CAT-18: Comentarios

```
G_COM = ({C, BODY, CHAR}, {/*, */, //, \n}, P, C)

P:
  C    → /* BODY */      (bloque C-style)
  C    → // BODY \n      (línea Python/Java-style)
  BODY → ε | BODY CHAR
  CHAR → cualquier carácter excepto los de cierre
```

---

## 6. Presencia de las 18 Categorías en LogiParse

Para cada categoría se indica si aparece **DIRECTAMENTE** (la GLC o su lenguaje
está modelado explícitamente en el código), **INDIRECTAMENTE** (el concepto subyace
en la implementación pero no en el DSL procesado), o **NO APARECE**.

### 6.1 Tabla de presencia

| #  | Categoría               | Presencia    | Justificación (referencia exacta)                                           |
|----|-------------------------|--------------|-----------------------------------------------------------------------------|
| 1  | Números                 | **DIRECTA**  | 5 tokens numéricos en `lexico.py` líneas 7-8,11-12,16                       |
| 2  | Identificadores         | **DIRECTA**  | `mis_codigos_orden` y `mis_nombres_producto` son identificadores estructurados |
| 3  | Expresiones aritméticas | **INDIRECTA**| Implícita en relación cantidad×precio=monto (S7 en `semantico.py` línea 95) |
| 4  | Expresiones relacionales| **INDIRECTA**| Usadas en validación S1–S10 en `semantico.py` (líneas 42,69,79,87,96...)   |
| 5  | Expresiones lógicas     | **INDIRECTA**| `len(ruc) == 11 and ruc.isdigit()` en `semantico.py` líneas 42,50          |
| 6  | Asignaciones            | **NO APARECE**| El DSL IDoc no tiene sintaxis de asignación                                |
| 7  | IF simple               | **INDIRECTA**| Estructuras if en `sintactico.py` (líneas 77,81,85) y `semantico.py`       |
| 8  | IF-ELSE                 | **INDIRECTA**| Ramificaciones if/else en todas las funciones del parser                   |
| 9  | WHILE                   | **NO APARECE**| No aparece en el DSL ni como construcción nombrada en la implementación    |
| 10 | FOR                     | **INDIRECTA**| `for num_linea, linea in enumerate(lineas, 1)` en `lexico.py` línea 39     |
| 11 | Lista de sentencias     | **DIRECTA**  | `items → item+` en `sintactico.py` — los ITM forman una lista de ítems     |
| 12 | Declaraciones           | **DIRECTA**  | `GRAMATICA` dict en `sintactico.py` líneas 9-45 declara tipos por posición |
| 13 | Funciones               | **NO APARECE**| No existe en el DSL IDoc procesado                                         |
| 14 | Parámetros              | **NO APARECE**| No existe en el DSL IDoc procesado                                         |
| 15 | Llamadas a funciones    | **NO APARECE**| No existe en el DSL IDoc procesado                                         |
| 16 | Cadenas balanceadas     | **NO APARECE**| No hay estructuras anidadas ni delimitadores pareados en IDoc              |
| 17 | Paréntesis balanceados  | **NO APARECE**| Mismo motivo que CAT-16                                                    |
| 18 | Comentarios             | **INDIRECTA**| El SQL generado en `traductor.py` incluye comentarios `--` (líneas 29,37)  |

### 6.2 Análisis detallado por categoría

#### CAT-1 y CAT-2 (Números e Identificadores) — PRESENCIA DIRECTA

Los 13 tokens de `lexico.py` incluyen cinco categorías numéricas:

- `mis_variables_ruc` (`^\d{11}$`) — número entero de longitud fija
- `mis_variables_fecha` (`^\d{8}$`) — número entero de longitud fija
- `mis_codigos_item` (`^\d{3}$`) — número entero de longitud fija
- `mis_variables_decimales` (`^\d+\.\d{2}$`) — número decimal
- `mis_variables_numericas` (`^\d+$`) — número entero variable

Y dos de tipo identificador:

- `mis_codigos_orden` (`^[A-Z]+-\d{4}-\d{3}$`) — identificador compuesto estructurado
- `mis_nombres_producto` (`^[a-z]+-[a-z]+$`) — nombre compuesto como identificador de producto

#### CAT-3 (Expresiones aritméticas) — PRESENCIA INDIRECTA

El formato IDoc **no incluye** expresiones aritméticas como texto en el archivo.
Sin embargo, la relación `cantidad × precio_unitario = subtotal` está **implícita**
en la estructura del documento y es verificada por la regla **S7** en `semantico.py`:

```python
# semantico.py, línea 95
monto_calculado = sum(int(itm[3]) * float(itm[5]) for itm in itm_data)
```

**¿En qué segmentos aparecerían expresiones aritméticas?**

- **ITM** (campos 4 y 6): `cantidad` y `precio` son los **operandos**
- **FTR** (campo 3): `monto_total` es el **resultado** de `Σ(cantidad_i × precio_i)`

Para el caso `ORD-2026-001.txt`:
```
ITM|001|aceite-vegetal|100|KG|15.50     →  100 × 15.50 = 1,550.00
ITM|002|harina-preparada|50|SAC|45.00  →   50 × 45.00 = 2,250.00
ITM|003|leche-evaporada|200|CAJA|32.00 →  200 × 32.00 = 6,400.00
FTR|3|10200.00|...                      →  Σ = 10,200.00  ✅
```

Si el sistema evolucionase para incluir expresiones en el archivo de entrada
(ej. `ITM|001|aceite-vegetal|50+50|KG|15.50`), se requeriría añadir la GLC
de CAT-3 al análisis sintáctico del campo `cantidad`.

#### CAT-11 (Lista de sentencias) — PRESENCIA DIRECTA

Las líneas `ITM` forman una **lista ordenada** de ítems. En `sintactico.py`:

```python
# sintactico.py, líneas 47-48
'items       → item+',
'item        → ITM | codigo_item | producto | cantidad | unidad | precio',
```

El operador `+` es la notación de la GLC para "uno o más", equivalente a:

```
items → item
items → items item    (recursión izquierda)
```

El validador en `sintactico.py` líneas 84-103 verifica que exista al menos
un ITM y que el orden HDR → ITM+ → FTR sea correcto.

#### CAT-12 (Declaraciones) — PRESENCIA DIRECTA

La estructura `GRAMATICA` en `sintactico.py` es literalmente un sistema de
tipos declarativo por posición:

```python
# sintactico.py, líneas 9-45
GRAMATICA = {
    'HDR': {'nombre': 'encabezado', 'campos': 7,
            'tipos': [['mis_segmentos_doc'], ['mis_codigos_orden'], ...]},
    'ITM': {'nombre': 'item', 'campos': 6,
            'tipos': [['mis_segmentos_doc'], ['mis_codigos_item'], ...]},
    'FTR': {'nombre': 'pie', 'campos': 4,
            'tipos': [['mis_segmentos_doc'], ['mis_variables_numericas', ...], ...]}
}
```

Cada entrada declara: el **número de campos**, el **nombre del segmento** y el
**tipo permitido por posición** — exactamente lo que haría una declaración de
estructura (`struct`) en un lenguaje de programación.

---

## 7. Árboles Sintácticos — Caso Real

### 7.1 GLC formal completa de LogiParse

Definida a partir de los nombres exactos de `core/sintactico.py`
(función `get_plantillas_gramatica` y diccionario `GRAMATICA`):

```
G_LogiParse = (N, Σ, P, documento)

N = {
  documento, encabezado, items, item, pie,
  segmento, codigo_orden, ruc_emisor, ruc_receptor, fecha, motivo, moneda,
  codigo_item, producto, cantidad, unidad, precio,
  total_items, monto_total, estado
}

Σ = {
  HDR, ITM, FTR, '|',
  <mis_codigos_orden>, <mis_variables_ruc>, <mis_variables_fecha>,
  <mis_motivos_traslado>, <mis_tipos_moneda>, <mis_codigos_item>,
  <mis_nombres_producto>, <mis_unidades_medida>, <mis_variables_decimales>,
  <mis_variables_numericas>, <mis_estados_orden>
}

P = {
  (1)  documento   → encabezado items pie
  (2)  items       → item
  (3)  items       → items item
  (4)  encabezado  → segmento SEP codigo_orden SEP ruc_emisor SEP ruc_receptor SEP fecha SEP motivo SEP moneda
  (5)  item        → segmento SEP codigo_item SEP producto SEP cantidad SEP unidad SEP precio
  (6)  pie         → segmento SEP total_items SEP monto_total SEP estado
  (7)  segmento    → <mis_segmentos_doc>
  (8)  codigo_orden → <mis_codigos_orden>
  (9)  ruc_emisor  → <mis_variables_ruc>
  (10) ruc_receptor → <mis_variables_ruc>
  (11) fecha       → <mis_variables_fecha>
  (12) motivo      → <mis_motivos_traslado>
  (13) moneda      → <mis_tipos_moneda>
  (14) codigo_item → <mis_codigos_item>
  (15) producto    → <mis_nombres_producto>
  (16) cantidad    → <mis_variables_numericas> | <mis_codigos_item>
  (17) unidad      → <mis_unidades_medida>
  (18) precio      → <mis_variables_decimales>
  (19) total_items → <mis_variables_numericas> | <mis_codigos_item>
  (20) monto_total → <mis_variables_decimales>
  (21) estado      → <mis_estados_orden>
}

S = documento
SEP = '|'  (terminal separador de campo)
```

> **Nota:** El separador `|` es un **terminal** del lenguaje IDoc — aparece
> literalmente en el archivo entre cada campo. Las producciones de `PRODUCCIONES`
> en `sintactico.py` usan `|` con doble rol (separador de campo Y separador BNF),
> lo cual es una notación informal. La GLC formal anterior usa `SEP` para distinguirlos.

### 7.2 Árbol sintáctico — Segmento HDR

**Entrada:** `HDR|ORD-2026-001|20100055237|20481559927|10062026|VENTA|PEN`

**Derivación:**
```
documento ⇒ encabezado items pie
          ⇒ encabezado ...
```

**Árbol:**
```
                                    encabezado
         |          |           |            |          |         |        |
     segmento  codigo_orden  ruc_emisor  ruc_receptor  fecha   motivo   moneda
         |           |           |            |           |        |        |
       [HDR]  [ORD-2026-001] [20100055237] [20481559927] [10062026] [VENTA] [PEN]
     mis_seg   mis_cod_ord   mis_var_ruc   mis_var_ruc  mis_fecha mis_mot mis_mon
```

**Producción aplicada:** `encabezado → segmento SEP codigo_orden SEP ruc_emisor SEP ruc_receptor SEP fecha SEP motivo SEP moneda`

### 7.3 Árbol sintáctico — Segmento ITM (línea 2)

**Entrada:** `ITM|001|aceite-vegetal|100|KG|15.50`

```
                              item
        |          |          |          |         |        |
    segmento  codigo_item  producto   cantidad   unidad   precio
        |          |           |          |         |        |
      [ITM]      [001]   [aceite-    [100]       [KG]    [15.50]
                          vegetal]
    mis_seg   mis_cod   mis_nom    mis_cod     mis_uni  mis_dec
              _item     _prod      _item*      _med     _imal
```

`*` — `100` clasifica como `mis_codigos_item` (3 dígitos, prioridad sobre `mis_variables_numericas`)

### 7.4 Árbol sintáctico — Segmento ITM (línea 3)

**Entrada:** `ITM|002|harina-preparada|50|SAC|45.00`

```
                                item
        |          |              |          |        |        |
    segmento  codigo_item      producto   cantidad  unidad   precio
        |          |              |           |        |        |
      [ITM]      [002]   [harina-preparada]  [50]    [SAC]  [45.00]
    mis_seg   mis_cod       mis_nom_prod    mis_num  mis_uni  mis_dec
              _item                         ↑
                                    mis_variables_numericas
                                    (solo 2 dígitos, no ^\d{3}$)
```

### 7.5 Árbol sintáctico — Segmento FTR

**Entrada:** `FTR|3|10200.00|PENDIENTE`

```
                          pie
         |           |           |            |
     segmento   total_items  monto_total    estado
         |           |           |             |
       [FTR]        [3]     [10200.00]    [PENDIENTE]
     mis_seg    mis_num     mis_dec       mis_est
               _ericas     _imal         _ado
```

### 7.6 Árbol sintáctico completo — documento ORD-2026-001.txt

```
                                        documento
                    ┌───────────────────────┼───────────────────────┐
               encabezado               items                      pie
                    │               ┌────────────┐                   │
                   [HDR...]         │            │                  [FTR...]
                                  item         items
                                  [ITM 003]      │
                                              ┌──┴──┐
                                            item   item
                                          [ITM 001] [ITM 002]
```

**Forma lineal equivalente** (derivación canónica por la izquierda):

```
documento
  ⇒  encabezado  items  pie                               (por prod. 1)
  ⇒  encabezado  items  item  pie                         (por prod. 3)
  ⇒  encabezado  items  item  item  pie                   (por prod. 3)
  ⇒  encabezado  item   item  item  pie                   (por prod. 2)
  ⇒  [HDR|ORD-2026-001|...|VENTA|PEN]                    (por prod. 4)
     [ITM|001|aceite-vegetal|100|KG|15.50]               (por prod. 5)
     [ITM|002|harina-preparada|50|SAC|45.00]             (por prod. 5)
     [ITM|003|leche-evaporada|200|CAJA|32.00]            (por prod. 5)
     [FTR|3|10200.00|PENDIENTE]                          (por prod. 6)
```

**Árbol expandido completo** (con todos los terminales):

```
                                             documento
                    ┌────────────────────────────┼────────────────────────────┐
               encabezado                      items                         pie
       ┌──┬──┬──┬──┬──┬──┐             ┌────────┴────────┐           ┌──┬──┬──┐
      seg  cod  r₁  r₂  fec  mot  mon  items             item       seg tot mon est
       |    |    |   |    |    |    |  ┌──┴──┐             |          |   |   |   |
     HDR  ORD- 201  204 1006 VEN  PEN item  item          ITM FTR   3 102  PEN
          2026  00  81  2026 TA        |     |             003        00.  DIENTE
          -001  55  55       |       ITM    ITM            |           00
               237  99      2026-    001   002
                    27      001

Lexemas terminales (hojas del árbol):
HDR, ORD-2026-001, 20100055237, 20481559927, 10062026, VENTA, PEN,
ITM, 001, aceite-vegetal, 100, KG, 15.50,
ITM, 002, harina-preparada, 50, SAC, 45.00,
ITM, 003, leche-evaporada, 200, CAJA, 32.00,
FTR, 3, 10200.00, PENDIENTE
```

### 7.7 Validación semántica sobre el árbol

Las 10 reglas semánticas de `semantico.py` operan sobre los **nodos del árbol**:

| Regla | Nodo(s) del árbol     | Verificación                                             | Resultado    |
|-------|-----------------------|----------------------------------------------------------|--------------|
| S1    | `ruc_emisor`          | `len("20100055237") == 11 and isdigit()`                 | ✅           |
| S2    | `ruc_receptor`        | `len("20481559927") == 11 and isdigit()`                 | ✅           |
| S3    | `fecha`               | `datetime.strptime("10062026", '%d%m%Y')` = 10/06/2026  | ✅           |
| S4    | `cantidad` (×3)       | `100 > 0`, `50 > 0`, `200 > 0`                          | ✅           |
| S5    | `precio` (×3)         | `15.50 > 0`, `45.00 > 0`, `32.00 > 0`                  | ✅           |
| S6    | `total_items` vs items| `int("3") == len([ITM001,ITM002,ITM003])`               | ✅ 3 = 3     |
| S7    | `monto_total` vs items| `\|10200.00 - (100×15.50 + 50×45.00 + 200×32.00)\| < 0.01`| ✅ 10200.00  |
| S8    | `motivo`              | `"VENTA" in {'VENTA','COMPRA','DEVOLUCION'}`            | ✅           |
| S9    | `moneda`              | `"PEN" in {'PEN','USD'}`                               | ✅           |
| S10   | `estado`              | `"PENDIENTE" in {'PENDIENTE','PROCESADO','ANULADO'}`   | ✅           |

---

## 8. Conclusión

### 8.1 La cadena compiladora completa en LogiParse

El caso `ORD-2026-001.txt` demuestra de forma concreta la secuencia canónica de
la teoría de compiladores aplicada a un DSL logístico real:

```
Archivo TXT                    Fase 1 — Análisis Léxico
──────────────                 (core/lexico.py)
HDR|ORD-2026-001|...    ──→    Lexemas + Tokens
ITM|001|aceite-...             [29 tokens clasificados]
...                                      │
                                         ▼
                               Fase 2 — Análisis Sintáctico
                               (core/sintactico.py)
                          ──→  Árbol Sintáctico
                               documento → encabezado items+ pie
                                         │
                                         ▼
                               Fase 3 — Análisis Semántico
                               (core/semantico.py)
                          ──→  Tabla de símbolos + Reglas S1-S10
                               Verificación de tipos y coherencia
                                         │
                                         ▼
                               Fase 4 — Generación de Código
                               (core/traductor.py)
                          ──→  SQL Server (3 sentencias INSERT)
```

### 8.2 Relación entre los formalismos

| Formalismo        | Función en LogiParse                                  | Implementación real              |
|-------------------|-------------------------------------------------------|----------------------------------|
| **Lexema**        | Unidad atómica del IDoc: `HDR`, `ORD-2026-001`, `100`| `linea.split('|')` en `lexico.py`|
| **Token**         | Categoría semántica del lexema                        | Lista `TOKENS` en `lexico.py`    |
| **Expresión Regular** | Patrón que define el lenguaje de cada token       | 13 regex en `TOKENS`             |
| **AFND**          | Reconocedor con ε-transiciones (modelo teórico)       | `AUTOMATAS_POR_TOKEN` por token  |
| **AFD**           | Implementación eficiente equivalente                  | `re.match()` en Python ≡ AFD     |
| **Tabla transición** | Representación tabular del AFD                     | `tabla` en `generador.py`        |
| **GLC**           | Define la estructura del documento IDoc               | `GRAMATICA` y `PRODUCCIONES`     |
| **Árbol sintáctico** | Estructura jerárquica instanciada de un documento | `arbol` devuelto por `sintactico`|
| **Semántica**     | Restricciones más allá de la sintaxis                 | S1–S10 en `semantico.py`         |
| **Traducción**    | Generación de código en lenguaje destino              | `traductor.py` → SQL Server      |

### 8.3 Posición de LogiParse en la jerarquía de Chomsky

```
┌────────────────────────────────────────────────────────┐
│  Tipo 0 — Lenguajes Recursivamente Enumerables (MT)    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tipo 1 — Sensibles al Contexto (MT Lineal)      │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Tipo 2 — Libres de Contexto (PDA)         │  │  │
│  │  │                                            │  │  │
│  │  │  ← LogiParse se ubica aquí (GLC)           │  │  │
│  │  │  GLC de documento IDoc (sintáctico.py)     │  │  │
│  │  │  ┌──────────────────────────────────────┐ │  │  │
│  │  │  │  Tipo 3 — Regulares (AFD/AFND)       │ │  │  │
│  │  │  │                                      │ │  │  │
│  │  │  │  ← Los 13 tokens (lexico.py)         │ │  │  │
│  │  │  │  cada token ≡ lenguaje regular       │ │  │  │
│  │  │  └──────────────────────────────────────┘ │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ← Máquina de Turing (generador.py) modela la    │  │
│  │    potencia computacional del transpilador        │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 8.4 Observaciones técnicas finales

1. **Equivalencia Kleene (ER ↔ AFD ↔ AFND):** Los 13 tokens definidos como
   expresiones regulares en `lexico.py` son exactamente los 13 AFD/AFND
   documentados en `automatas/generador.py`. La función `re.match()` de Python
   implementa internamente un DFA minimizado — el equivalente computacional
   exacto de los autómatas descritos.

2. **La GLC no es ambigua:** La estructura IDoc (HDR exactamente primero, FTR
   exactamente al final, ITM+ en el medio) define una gramática determinista
   LL(1) — cada segmento es identificado por su primer token (`mis_segmentos_doc`),
   sin necesidad de backtracking.

3. **Separación limpia de fases:** LogiParse implementa el principio clásico de
   los compiladores: léxico captura lexemas, sintáctico verifica estructura,
   semántico verifica coherencia de dominio, y el traductor genera el código
   destino. Ninguna fase asume responsabilidades de otra.

4. **Alcance semántico vs. sintáctico:** Los RUC de 11 dígitos son *léxicamente*
   cadenas de dígitos (`^\d{11}$`) y *sintácticamente* campos de tipo `ruc_emisor`
   o `ruc_receptor`. Su validez *semántica* (que sean contribuyentes reales) está
   más allá del alcance del sistema — LogiParse verifica solo la forma, no la
   existencia en el padrón de SUNAT.

5. **Extensibilidad:** Para soportar expresiones aritméticas en los campos
   `cantidad` (ej. `50+50`), bastaría añadir la GLC de CAT-3 a la producción
   de `cantidad` en `sintactico.py` y un evaluador en `semantico.py`. El
   diseño actual lo permite sin modificar las otras fases.

---

*Documento generado con base en análisis directo de código fuente.*  
*Fuentes verificadas: `core/lexico.py` (13 tokens), `core/sintactico.py` (15 producciones),*  
*`core/semantico.py` (10 reglas S1–S10), `core/traductor.py` (3 INSERT), `automatas/generador.py`*  
*(12 autómatas por token + 1 global + 1 Máquina de Turing).*
