# FormationDSL

## Palabras Reservadas

- definitions -> region de definir formaciones
- groups -> region de definir alias de grupos
- begin -> regin de definicion de pasos
- end -> fin de los pasos
- line_up -> orden de formacion
- with -> asignacion deun grupo a una formacion
- in -> asignacion de traslacion
- heading -> asignacion de rotacion
- args -> argumentos extras a pasar
- def -> definir funcion
- G -> grupo
- while -> ciclo
- step -> formaciones
- if/else -> condicional
- allof -> iterador de grupo
- of -> relacion entre personas de un grupo
- at -> relacion de direccion
- prev\next -> referencias a personas antes y detras en grupos
- from -> instruccion sobre elementos de un grupo
- take -> tomar cierta cantidad de miembros de un grupo
- borrow\starting_at\to -> traspaso de personas de un grupo a otro

### tipos

- vector -> tupla
- [] -> array
- bool -> booleano
- int -> entero
- group -> grupo

### vecotres direccionales built-in

- up
- down
- left
- rigth

## Apariencia del script

``` python
definitions

    def <name_of_formation> (<type_of_param> <name_of_param>, ...)
    {   
        <body>
    }

    ...

groups 

    <alias_of_group> = <identifier1>, <identifier2>, ... 

    ...

begin 

    step 
        line_on <name_of_formation> with <alias_of_gropu> in <vector> heading <direction> args (<param1>, <param2>, ...)

        ...

    ...

end
```


## Gramatica

S -> *definition* D *groups* G *begin_with* *num* R *end* $

D -> *def* *identifier* ( P ) { B } D | epsilon

P -> *type* *identifier* P1 | epsilon

P1 -> ,*type* *identifier* P1 | epsilon

B -> A B | *while* ( BExp ) { B } B | *if* ( BExp ) { B } ELSE B | *all_of* *identifier* *at* VExp *of* *r_poss* B | *from* *identifier* *borrow* IExp *starting_at* IExp *to* *identifier* B | *node* VExp *of* *node* B | *identifier*(ARG) | *identifier*.*identifier*(ARG) | epsilon

A -> *type* *identifier* = As | *identifier*[ IExpr ] = As  | *identifier* = As  | *type* *identifier* = *from* *identifier* *take* IExp *starting_at* IExp

As -> M | I | *identifier*.*identifier*(ARG) | *identifier*[ IExpr ]


BExp ->  *not* BExp | BTerm B2Exp | ( BExp ) B2Exp

B2Exp -> *and* BExp | *or* BExp | epsilon

BTerm -> *identifier* | *true* | *false* | IExp == IExp | V == V | IExp >= IExp | IExp <= IExp | IExp < IExp | IExp > IExp

ELSE -> *else* { B } | epsilon



IExp -> T X

X -> + IExp X | - IExp X | epsilon

T -> F Y

Y -> * F Y | // F Y | % F Y | epsilon

F -> *num* | ( IExp ) | *identifier*

N -> IExp | epsilon



VExp -> VT XV

XV -> + VExp XV | - VExp XV | * IExp |  epsilon

VT -> (IExp, IExp) | (VExp) | *identifier* | *dir* N



R -> *line_up* *identifier* *with* [ ] *in* VExp *heading* *dir* *args* ARG RN

RN -> *step* R | R | epsilon

ARG -> M ARG | ,M ARG | epsilon

M -> BExp | IExp | VExp

G -> *identifier* = I

I -> [*num* I2] | [*num* : *num*]

I2 -> , *num* I2 | epsilon

