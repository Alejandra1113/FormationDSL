# FormationDSL

Este DSL está dirigido al trabajo con formaciones de individuos. El lenguaje permite crear formaciones para `grupos` mediante instrucciones que facilitan la
declaración de la formacion a partir de relaciones entre los miembros de un grupo. El código consta de 3 regiones fundamentales: Declaraciones de formaciones, Declaraciones de grupos, Declaraciones de rutinas de formaciones, marcadas con las palabras claves definitions, groups, begin_with respectivamente. Para las definiciones de formaciones se tiene una variable `group G` que no es necesaria escribirla como parámetro pues se asume que para tener una formación se tiene que tener un grupo.  

# Sobre el DSL
## Palabras Reservadas y Operaciones Build In

- definitions -> región de definir formaciones
- groups -> región de definir alias de grupos
- begin_with -> región de definicion de pasos
- end -> fin de los pasos
- line_up - with - in - heading - args  -> orden de formación
- def -> definir función
- G -> grupo
- while -> ciclo
- step -> formaciones
- if \ else -> condicional
- all_of - at - of -> iterador de grupo estableciendo relaciones entre los miembros
- prev \ next -> referencias a personas antes y detras en grupos
- from - take - starting_at -> tomar cierta cantidad de miembros de un grupo para crear una partición en dos subgrupos
- from - borrow - starting_at - to -> traspaso de personas de un grupo a otro
- up \ down \ left \ right \ up-left \ up-right \ down-left \ down-right -> vectores basicos direccionales
  
## Tipos

- vector -> tupla de enteros
- bool -> booleano
- int -> entero
- group -> grupo
- \[ \] -> array

## Apariencia del script

``` python
definitions

    def dos_filas()
    {
        int temp  = G.len() // 2
        int resto = G.len() % 2
        int i = 0
        while(i < temp + resto)
        {
            if(i < temp - 1)
            {
                G[temp + 1] down of G[i]
            }
            if( i > 0)
            {
                G[temp + i - 1] left of G[temp + 1]
            }
        }
    }

    def <name_of_formation> (<type_of_param> <name_of_param>, ...)
    {   
        <body>
    }

    ...

groups 

    <alias_of_group_1> = [ <int_value> ,<int_value> , ... ]
    <alias_of_group_2> = [ <int_value> : <int_value> ]
    ...

begin_with <int_value> 
        
        line_on <name_of_formation> with <alias_of_group_1> in <vector> heading <direction> args(<param1>, <param2>, ...)
        line_on <name_of_formation> with <alias_of_group_2> in <vector> heading <direction> args(<param1>, <param2>, ...)

        ...
step 
        line_on <name_of_formation> with <alias_of_group_1> in <vector> heading <direction> args(<param1>, <param2>, ...)
        line_on <name_of_formation> with <alias_of_group_2> in <vector> heading <direction> args(<param1>, <param2>, ...)
        
        ...
step 
        ...

...

end
```

# Gramática

Para definir la gramática utilizamos la clase `Grammar` provista en las clases prácticas, la que fue incorporada al proyecto en el archivo `pycompiler.py`. Las producciones, terminales y no terminales de nustra gramática para el DSL se muestran detalladamente
en el siguiente listado, su equivalente en código se encuentra en el archivo `Grammar.py` donde además se especifica el comportamiento de cada producción al sintetizar los valores mediante una gramática atributada.

`start`

S -> *definition* D *begin_with* *num* R *end* 

`definitions`

D -> *def* *id* ( P ) { B } D\
D -> epsilon


`params` 

P -> *type* *id* P1 \
P -> *type* \[ \] *id* P1 \
p -> epsilon

P1 -> , *type* *id* P1\
P1 -> , *type* \[ \] *id* P1\
P1 -> epsilon

`body`

B -> A B\
B -> *while* ( BExp ) { B BRK } B\
B -> *if* ( BExp ) { B BRK } ELSE B\
B -> *all_of* *id* *at* BE *of* *r_poss* B\
B -> *from* *id* *borrow* BE *starting_at* BE *to* *id* B\
B -> *id*\[ E \] BE *of* *id*\[ E \] B\
B -> *id*( ARG ) B\
B -> *id*.*id*( ARG ) B\
B -> epsilon\
B -> return

`breaks`

BRK -> break\
BRK -> continue\
BRK -> epsilon

`else`

ELSE -> *else* { B BRK}\
ELSE -> epsilon

`asign`

A -> *type* *id* = As\
A -> *type* \[ \] *id* = As\
A -> *id*[ E ] = As\
A -> *id* = As\
A -> *type* *id* = *from* *id* *take* BE *starting_at* BE

AS -> BE\
AS -> *id*(ARG)\
AS -> [ ARR ]

`arrays`

ARR -> E ARR1\
ARR -> epsilon

ARR1 -> , E ARR1\
ARR1 -> epsilon

`steps`

R -> *line_up* *id* *with* I *in* BE *heading* *dir* *args* ARG RN

RN -> *step* R\
RN -> R\
RN -> epsilon

`arguments`

ARG -> BE ARG1\
ARG -> epsilon

ARG1 -> , BE ARG1\
ARG1 -> epsilon

`iter`

I -> [*num* I2]\
I -> [*num* : *num*]

I2 -> , *num* I2\
I2 -> epsilon

`boolean`

BE -> C and BE\
BE -> C or BE\
BE -> not BE\
BE -> C

`comparations`

C -> E == C\
C -> E != C\
C -> E <= C\
C -> E >= C\
C -> E > C\
C -> E < C\
C -> E

`expresions`

E -> E + T\
E ->E - T\
E ->T

`terms`

T -> T * F\
T -> T / F\
T -> T % F\
T -> F

`factors`

F -> bool\
F -> num\
F -> V\
F -> *id*\
F -> *id*.*id*( ARG )\
F -> *id*[ E ]\
F -> ( BE )
F -> direc

`vectors`

V -> ( E, E )

# Tokenizer

Para tokenizar la cadena de entrada se utilizaron expresiones regulares del módulo 
`re` de Python para hacer match con secciones del texto y trasnformarlas en los Tokens correspondientes. Para crear un Token se utilizó la clase `Token` provista en clase práctica, la cual fue extendida con la información correspondiente a la fila y columna del token para mayor descripción a la hora de detectar errores de parsing.

En una fase previa a tokenizar, se hace un preprocesado del código, en el que se reemplazan los alias de grupos definidos en la sección `groups` por sus valores literales en las instrucciones `line_on`, de modo que el ejemplo de código inicial luego del preprocesado queda de la sigiente forma

``` python
definitions

    def dos_filas()
    { ... }

    def <name_of_formation> (<type_of_param> <name_of_param>, ...)
    { ... }

    ...

begin_with <int_value> 
        
        line_on <name_of_formation> with [ <int_value> ,<int_value> , ... ] in <vector> heading <direction> args(<param1>, <param2>, ...)
        line_on <name_of_formation> with [ <int_value> : <int_value> ] in <vector> heading <direction> args(<param1>, <param2>, ...)

        ...
step 
        line_on <name_of_formation> with [ <int_value> ,<int_value> , ... ] in <vector> heading <direction> args(<param1>, <param2>, ...)
        line_on <name_of_formation> with [ <int_value> : <int_value> ] in <vector> heading <direction> args(<param1>, <param2>, ...)
        
        ...
step 
        ...

...

end
```

Esta nueva cadena de código se tokeniza con el método `tokenize`, los `fixed_tokens` y  `variable_tokens` presentes en `Tokenizer.py`
# Parser

Para parsear la gramática utilizamos un parser LR(1), para esto utilizamos las clases `ShiftReduceParser` y `LR1Parser` que fueron completadas de los ejercicios propuestos en clase práctica. En el cómputo de la tablas goto y action se utilizaron los métodos auxiliares para determinar los firsts y la clausura para construir el autómata, todos estos se encuentran en el archivo `automata.py` y el parser en `Parser.py`.

Como el autómata generado por la gramática se utiliza solo para generar las tablas de goto y actions, y computarlo es costoso, se guardan las tablas en los archivos `actions` y `goto` para no tener que generarlas en cada proceso de parsing.
# AST

La construccion del AST se realiza en paralelo al proceso de parsing, se aprovecha que la gramática es LR(1) para llevar una pila en la que se van incluyendo nodos con cada SHIFT y en la que se sacan los nodos y se pasan como valores sintetizados para la construcción de otros nodosen cada REDUCE.

Para los nodos se estableció una jerarquía, basada en la propuesta en clase práctica y enriquecida con nuevos nodos específicos del DSL como los `BorrowNode`, `BeginNode`, `LinkNode`, entre otros. Estas clases se encuentran en `semantic\languaje.py`
# Checkeo Semántico y de Tipos

Para hacer el checkeo de tipos, así como que solo se llamen funciones definidas y el uso de variables declaradas se utilizó el patrón de diseño Visitor. Como el DSL es de tipado estático se programó una jerarquia de clases que responden a los tipos permitidos (int, bool, vector, group y array) los cuales se encuentran en `semantic\types.py` y haciendo uso de las mismas se revisa con el `visitor\chk_type.py` que las operaciones realizadas en tre tipos sean correctas.

Con el chequeo 
# Generación de código Python 
