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
