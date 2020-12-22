from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))
import analizer.ply.yacc as yacc
from analizer.tokens import *

# Prueba para dataframe:
import analizer.abstract.select_data as data

df = data.dataSelect()
df.crossJoin()

# Construccion del analizador léxico
import analizer.ply.lex as lex

lexer = lex.lex()
# Asociación de operadores y precedencia

repGrammar = []
precedence = (
    ("left", "R_UNION", "R_INTERSECT", "R_EXCEPT"),
    ("right", "R_NOT"),
    ("left", "R_AND", "R_OR"),
    (
        "left",
        "R_BETWEEN",
        "R_IS",
    ),
    (
        "left",
        "S_IGUAL",
        "OL_DISTINTODE",
        "OL_MAYORQUE",
        "OL_MENORQUE",
        "OL_MAYORIGUALQUE",
        "OL_MENORIGUALQUE",
    ),
    ("left", "OC_CONCATENAR"),
    ("left", "O_SUMA", "O_RESTA"),
    ("left", "O_PRODUCTO", "O_DIVISION", "O_MODULAR"),
    ("right", "UO_SUMA", "UO_RESTA"),
    ("left", "O_EXPONENTE"),
)

# Definición de la gramática

import analizer.abstract.expression as expression
import analizer.abstract.instruction as instruction


def p_init(t):
    """init : stmtList"""
    t[0] = t[1]
    global repGrammar
    repGrammar = []
    repGrammar.append(t.slice)


def p_stmt_list(t):
    """stmtList : stmtList stmt"""
    t[1].append(t[2])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_stmt_u(t):
    """stmtList : stmt"""
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_stmt(t):
    """
    stmt : createStmt  S_PUNTOCOMA
        | showStmt S_PUNTOCOMA
        | alterStmt S_PUNTOCOMA
        | dropStmt S_PUNTOCOMA
        | insertStmt S_PUNTOCOMA
        | updateStmt S_PUNTOCOMA
        | deleteStmt S_PUNTOCOMA
        | truncateStmt S_PUNTOCOMA
        | useStmt S_PUNTOCOMA
        | selectStmt S_PUNTOCOMA
    """
    try:
        t[0] = t[1].execute(None)
    except:
        return
    repGrammar.append(t.slice)


# Statement para el CREATE
# region CREATE
def p_id_string(t):
    """
    idOrString : ID
    | STRING
    | CHARACTER
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_createstmt(t):
    """createStmt : R_CREATE createBody"""
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_createbody(t):
    """
    createBody : createOpts
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_createopts_table(t):
    """createOpts : R_TABLE ifNotExists idOrString S_PARIZQ createTableList S_PARDER inheritsOpt """
    t[0] = instruction.CreateTable(t[2], t[3], t[7], t[5])
    repGrammar.append(t.slice)


def p_createopts_db(t):
    """
    createOpts : orReplace R_DATABASE ifNotExists idOrString createOwner createMode
    """
    t[0] = instruction.CreateDatabase(t[1], t[3], t[4], t[5], t[6])
    repGrammar.append(t.slice)


def p_replace_true(t):
    """
    orReplace : R_OR R_REPLACE
    """
    t[0] = True
    repGrammar.append(t.slice)


def p_replace_false(t):
    """
    orReplace :
    """
    t[0] = False
    repGrammar.append(t.slice)


def p_createopts_type(t):
    """
    createOpts : R_TYPE ifNotExists ID R_AS R_ENUM S_PARIZQ paramsList S_PARDER
    """
    t[0] = instruction.CreateType(t[2], t[3], t[7])
    repGrammar.append(t.slice)


def p_ifnotexists_true(t):
    """
    ifNotExists : R_IF R_NOT R_EXISTS
    """
    t[0] = True
    repGrammar.append(t.slice)


def p_ifnotexists_false(t):
    """
    ifNotExists :
    """
    t[0] = False
    repGrammar.append(t.slice)


def p_inheritsOpt(t):
    """
    inheritsOpt : R_INHERITS S_PARIZQ ID S_PARDER
    """
    t[0] = t[3]
    repGrammar.append(t.slice)


def p_inheritsOpt_none(t):
    """
    inheritsOpt :
    """
    t[0] = None
    repGrammar.append(t.slice)


def p_createowner(t):
    """
    createOwner : R_OWNER ID
    | R_OWNER STRING
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_createowner_asg(t):
    """
    createOwner :  R_OWNER S_IGUAL ID
    | R_OWNER S_IGUAL STRING
    """
    t[0] = t[3]
    repGrammar.append(t.slice)


def p_createowner_none(t):
    """
    createOwner :
    """
    t[0] = None
    repGrammar.append(t.slice)


def p_createmode(t):
    """
    createMode : R_MODE INTEGER
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_createMode_asg(t):
    """
    createMode : R_MODE S_IGUAL INTEGER
    """
    t[0] = t[3]
    repGrammar.append(t.slice)


def p_createmode_none(t):
    """
    createMode :
    """
    t[0] = None
    repGrammar.append(t.slice)


def p_createtable_list(t):
    """createTableList : createTableList S_COMA createTable"""
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_createtable_u(t):
    """createTableList :  createTable"""
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_createTable_id(t):
    """
    createTable :  ID types createColumns
    """
    t[0] = [False, t[1], t[2], t[3]]
    repGrammar.append(t.slice)


def p_createTable(t):
    """
    createTable : createConstraint
    | createUnique
    | createPrimary
    | createForeign
    """
    t[0] = [True, t[1]]
    repGrammar.append(t.slice)


def p_createColumNs(t):
    """
    createColumns : colOptionsList
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_createColumNs_none(t):
    """
    createColumns :
    """
    t[0] = None
    repGrammar.append(t.slice)


def p_createConstraint(t):
    """createConstraint : constrName R_CHECK S_PARIZQ booleanCheck S_PARDER"""
    t[0] = [t[2], t[1], t[4]]
    repGrammar.append(t.slice)


def p_createUnique(t):
    """createUnique : R_UNIQUE S_PARIZQ idList S_PARDER"""
    t[0] = [t[1], t[3]]
    repGrammar.append(t.slice)


def p_createPrimary(t):
    """createPrimary : R_PRIMARY R_KEY S_PARIZQ idList S_PARDER"""
    t[0] = [t[1], t[4]]
    repGrammar.append(t.slice)


def p_createForeign(t):
    """
    createForeign : R_FOREIGN R_KEY S_PARIZQ idList S_PARDER R_REFERENCES ID S_PARIZQ idList S_PARDER
    """
    t[0] = [t[1], t[4], t[7], t[9]]
    repGrammar.append(t.slice)


def p_createForeign_op2(t):
    """
    createForeign : R_FOREIGN R_KEY S_PARIZQ idList S_PARDER R_REFERENCES ID
    """
    t[0] = [t[1], t[4], t[7]]
    repGrammar.append(t.slice)


def p_constrName(t):
    """
    constrName : R_CONSTRAINT ID
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_constrName_none(t):
    """
    constrName :
    """
    t[0] = None
    repGrammar.append(t.slice)


def p_id_list(t):
    """idList : idList S_COMA ID"""
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_id_u(t):
    """idList : ID"""
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_types(t):
    """
    types :  ID
    """
    t[0] = [t[1], [None]]
    repGrammar.append(t.slice)


def p_types_simple(t):
    """
    types : T_SMALLINT
    | T_INTEGER
    | T_BIGINT
    | T_REAL
    | T_DOUBLE T_PRECISION
    | T_MONEY
    | T_TEXT
    | T_BOOLEAN
    | R_TIMESTAMP
    | T_DATE
    | T_TIME
    """
    t[0] = [t[1], [None]]
    repGrammar.append(t.slice)


# TODO: Cambiar el optParams
def p_types_params(t):
    """
    types : T_DECIMAL optParams
    | T_NUMERIC optParams
    | T_VARCHAR optParams
    | T_CHARACTER optParams
    | T_CHAR optParams
    """
    t[0] = [t[1], t[2]]
    repGrammar.append(t.slice)


def p_types_var(t):
    """
    types : T_CHARACTER T_VARYING optParams
    """
    t[0] = [t[2], t[3]]
    repGrammar.append(t.slice)


def p_timeType_interval(t):
    """
    types : R_INTERVAL intervalFields
    """
    t[0] = [t[1], [t[2]]]
    repGrammar.append(t.slice)


def p_intervalFields(t):
    """
    intervalFields :  R_YEAR
    | R_MONTH
    | R_DAY
    | R_HOUR
    | R_MINUTE
    | R_SECOND
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_intervalFields_none(t):
    """
    intervalFields :
    """
    t[0] = False
    repGrammar.append(t.slice)


def p_optParams(t):
    """optParams : S_PARIZQ literalList S_PARDER"""
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_optParams_none(t):
    """optParams : """
    t[0] = None
    repGrammar.append(t.slice)


def p_colOptions_list(t):
    """colOptionsList : colOptionsList colOptions"""
    t[1].append(t[2])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_colOptions_u(t):
    """colOptionsList : colOptions"""
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_colOptions(t):
    """
    colOptions : defaultVal
    | nullOpt
    | constraintOpt
    | primaryOpt
    | referencesOpt
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


# cambiar literal
def p_defaultVal(t):
    """defaultVal : R_DEFAULT literal"""
    t[0] = [t[1], t[2].execute(0)]
    repGrammar.append(t.slice)


def p_nullOpt_true(t):
    """
    nullOpt : R_NOT R_NULL
    """
    t[0] = [t[2], True]
    repGrammar.append(t.slice)


def p_nullOpt_false(t):
    """
    nullOpt : R_NULL
    """
    t[0] = [t[1], False]
    repGrammar.append(t.slice)


# cambiar literal


def p_constraintOpt_unique(t):
    """
    constraintOpt : constrName R_UNIQUE
    """
    if t[1] == None:
        t[0] = [t[2]]
    else:
        t[0] = None
    repGrammar.append(t.slice)


def p_constraintOpt_check(t):
    """
    constraintOpt : constrName R_CHECK S_PARIZQ booleanCheck S_PARDER
    """
    t[0] = [t[2], t[1], t[4]]
    repGrammar.append(t.slice)


def p_primaryOpt(t):
    """primaryOpt : R_PRIMARY R_KEY"""
    t[0] = [t[1], True]
    repGrammar.append(t.slice)


def p_referencesOpt(t):
    """referencesOpt : R_REFERENCES ID"""
    t[0] = [t[1], t[2]]
    repGrammar.append(t.slice)


# endregion CREATE

# Gramatica para expresiones

# region Expresiones
def p_expresion(t):
    """
    expresion : datatype
            | expBool
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_expresion_(t):
    """
    expresion : S_PARIZQ selectStmt S_PARDER
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_funcCall_1(t):
    """
    funcCall : ID S_PARIZQ paramsList S_PARDER
    """
    t[0] = expression.FunctionCall(t[1], t[3], t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


def p_funcCall_2(t):
    """
    funcCall : ID S_PARIZQ S_PARDER
            | R_NOW S_PARIZQ S_PARDER
    """
    t[0] = expression.FunctionCall(t[1], [], t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


def p_funcCall_3(t):
    """
    funcCall : R_COUNT S_PARIZQ datatype S_PARDER
            | R_COUNT S_PARIZQ O_PRODUCTO S_PARDER
            | R_SUM S_PARIZQ datatype S_PARDER
            | R_PROM S_PARIZQ datatype S_PARDER
    """
    repGrammar.append(t.slice)
    t[0] = expression.AggregateFunction(t[1], t[3], t.slice[1].lineno, t.slice[1].lexpos)

def p_extract_1(t):
    """
    extract : R_EXTRACT S_PARIZQ optsExtract R_FROM timeStamp S_PARDER
    """
    t[0] = expression.ExtractDate(
        t[3], t[5][0], t[5][1], t.slice[1].lineno, t.slice[1].lexpos
    )

    repGrammar.append(t.slice)


def p_extract_2(t):
    """
    extract : R_EXTRACT S_PARIZQ optsExtract R_FROM columnName S_PARDER
    """
    t[0] = expression.ExtractColumnDate(
        t[3], t[5], t.slice[1].lineno, t.slice[1].lexpos
    )
    repGrammar.append(t.slice)


def p_timeStamp(t):
    """
    timeStamp : R_TIMESTAMP STRING
          | R_INTERVAL STRING
    """
    t[0] = [t[1], t[2], t.slice[1].lineno, t.slice[1].lexpos]
    repGrammar.append(t.slice)


def p_optsExtract(t):
    """
    optsExtract : R_YEAR
                  | R_MONTH
                  | R_DAY
                  | R_HOUR
                  | R_MINUTE
                  | R_SECOND
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_datePart(t):
    """
    datePart : R_DATE_PART S_PARIZQ STRING S_COMA dateSource S_PARDER
    """
    t[0] = expression.DatePart(
        t[3], t[5][0], t[5][1], t.slice[1].lineno, t.slice[1].lexpos
    )
    repGrammar.append(t.slice)


def p_dateSource(t):
    """
    dateSource : R_TIMESTAMP STRING
          | T_DATE STRING
          | T_TIME STRING
          | R_INTERVAL STRING
          | R_NOW S_PARIZQ S_PARDER
    """
    t[0] = [t[1], t[2]]
    repGrammar.append(t.slice)


def p_current(t):
    """
    current : R_CURRENT_DATE
          | R_CURRENT_TIME
    """
    t[0] = expression.Current(t[1], None, t.slice[1].lineno, t.slice[1].lexpos)

    repGrammar.append(t.slice)


def p_current_1(t):
    """
    current : timeStamp
    """
    t[0] = expression.Current(t[1][0], t[1][1], t[1][2], t[1][3])
    repGrammar.append(t.slice)


def p_literal_list(t):
    """literalList : literalList S_COMA literal"""
    t[1].append(t[3].execute(0).value)
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_literal_u(t):
    """literalList : literal"""
    t[0] = [t[1].execute(0).value]
    repGrammar.append(t.slice)


def p_literal(t):
    """
    literal :  INTEGER
    | STRING
    | DECIMAL
    | CHARACTER
    | R_TRUE
    | R_FALSE
    | R_NULL
    """
    if t.slice[1].type == "CHARACTER" or t.slice[1].type == "STRING":
        tipo = expression.TYPE.STRING
    elif t.slice[1].type == "R_TRUE" or t.slice[1].type == "R_FALSE":
        t.slice[1].value = t.slice[1].value == "TRUE"
        tipo = expression.TYPE.BOOLEAN
    elif t.slice[1].type == "R_NULL":
        tipo = expression.TYPE.NULL
    else:
        tipo = expression.TYPE.NUMBER
    t[0] = expression.Primitive(
        tipo, t.slice[1].value, t.slice[1].value, t.slice[1].lineno, t.slice[1].lexpos
    )

    repGrammar.append(t.slice)


def p_params_list(t):
    """paramsList : paramsList S_COMA datatype"""
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_params_u(t):
    """paramsList : datatype"""
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_datatype_operadores_binarios1(t):
    """
    datatype : datatype O_SUMA datatype
    | datatype O_RESTA datatype
    | datatype O_PRODUCTO datatype
    | datatype O_DIVISION datatype
    | datatype O_EXPONENTE datatype
    | datatype O_MODULAR datatype
    """
    t[0] = expression.BinaryArithmeticOperation(t[1], t[3], t[2], t[1].row, t[1].column)

    repGrammar.append(t.slice)


def p_datatype_operadores_binarios2(t):
    """
    datatype : datatype OC_CONCATENAR datatype
    """
    t[0] = expression.BinaryStringOperation(t[1], t[3], t[2], t[1].row, t[1].column)
    repGrammar.append(t.slice)


def p_datatype_operadores_unarios(t):
    """
    datatype : O_RESTA datatype %prec UO_RESTA
    | O_SUMA datatype %prec UO_SUMA
    """
    t[0] = expression.UnaryArithmeticOperation(t[2], t[1], t[2].row, t[2].column)
    repGrammar.append(t.slice)


def p_datatype_operandos(t):
    """
    datatype : columnName
    | literal
    | funcCall
    | extract
    | datePart
    | current
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_datatype_agrupacion(t):
    """
    datatype : S_PARIZQ datatype S_PARDER
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_expCompBinario_1(t):
    """
    expComp : datatype OL_MENORQUE datatype
    | datatype OL_MAYORQUE datatype
    | datatype OL_MAYORIGUALQUE datatype
    | datatype OL_MENORIGUALQUE datatype
    | datatype S_IGUAL datatype
    | datatype OL_DISTINTODE datatype
    """
    t[0] = expression.BinaryRelationalOperation(t[1], t[3], t[2], t[1].row, t[1].column)
    repGrammar.append(t.slice)


def p_expCompBinario_2(t):
    """
    expComp : datatype R_IS R_DISTINCT R_FROM datatype
    """
    t[0] = expression.BinaryRelationalOperation(
        t[1], t[5], t[2] + t[3] + t[4], t[1].row, t[1].column
    )
    repGrammar.append(t.slice)


def p_expCompBinario_3(t):
    """
    expComp : datatype R_IS R_NOT R_DISTINCT R_FROM datatype
    """
    t[0] = expression.BinaryRelationalOperation(
        t[1], t[6], t[2] + t[3] + t[4] + t[5], t[1].row, t[1].column
    )
    repGrammar.append(t.slice)


def p_expComp_ternario_1(t):
    """
    expComp :  datatype R_BETWEEN datatype R_AND datatype
    """
    t[0] = expression.TernaryRelationalOperation(
        t[1], t[3], t[5], t[2], t[1].row, t[1].column
    )
    repGrammar.append(t.slice)


def p_expComp_ternario_2(t):
    """
    expComp : datatype R_NOT R_BETWEEN datatype R_AND datatype
    | datatype R_BETWEEN R_SYMMETRIC datatype R_AND datatype
    """
    t[0] = expression.TernaryRelationalOperation(
        t[1], t[4], t[6], t[2] + t[3], t[1].row, t[1].column
    )

    repGrammar.append(t.slice)


def p_expComp_unario_1(t):
    """
    expComp : datatype R_ISNULL
    | datatype R_NOTNULL
    """
    t[0] = expression.UnaryRelationalOperation(t[1], t[2], t[1].row, t[1].column)

    repGrammar.append(t.slice)


def p_expComp_unario_2(t):
    """
    expComp : datatype R_IS R_NULL
    | datatype R_IS R_TRUE
    | datatype R_IS R_FALSE
    | datatype R_IS R_UNKNOWN
    """
    t[0] = expression.UnaryRelationalOperation(t[1], t[2] + t[3], t[1].row, t[1].column)
    repGrammar.append(t.slice)


def p_expComp_unario_3(t):
    """
    expComp : datatype R_IS R_NOT R_NULL
    | datatype R_IS R_NOT R_TRUE
    | datatype R_IS R_NOT R_FALSE
    | datatype R_IS R_NOT R_UNKNOWN
    """
    t[0] = expression.UnaryRelationalOperation(
        t[1], t[2] + t[3] + t[4], t[1].row, t[1].column
    )
    repGrammar.append(t.slice)


def p_expSubq(t):
    """
    expSubq : datatype OL_MENORQUE  subqValues S_PARIZQ selectStmt S_PARDER
              | datatype OL_MAYORQUE  subqValues S_PARIZQ selectStmt S_PARDER
              | datatype OL_MAYORIGUALQUE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype OL_MENORIGUALQUE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype OL_ESIGUAL  subqValues S_PARIZQ selectStmt S_PARDER
              | datatype OL_DISTINTODE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_BETWEEN datatype R_AND datatype subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_NOT R_BETWEEN datatype R_AND datatype subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_BETWEEN R_SYMMETRIC datatype R_AND datatype subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_DISTINCT R_FROM datatype subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NOT R_DISTINCT R_FROM datatype subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NULL subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NOT R_NULL subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_ISNULL subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_NOTNULL subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_TRUE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NOT R_TRUE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_FALSE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NOT R_FALSE subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_UNKNOWN subqValues S_PARIZQ selectStmt S_PARDER
              | datatype R_IS R_NOT R_UNKNOWN subqValues S_PARIZQ selectStmt S_PARDER
              | stringExp R_LIKE STRING
    """
    repGrammar.append(t.slice)


def p_stringExp(t):
    """
    stringExp : STRING
          | columnName
    """
    repGrammar.append(t.slice)


def p_subqValues(t):
    """
    subqValues : R_ALL
                  | R_ANY
                  | R_SOME
    """
    repGrammar.append(t.slice)


def p_boolean_1(t):
    """
    boolean : R_EXISTS S_PARIZQ selectStmt S_PARDER
            | datatype R_IN S_PARIZQ selectStmt S_PARDER
            | datatype R_NOT R_IN S_PARIZQ selectStmt S_PARDER
    """
    repGrammar.append(t.slice)


def p_boolean_2(t):
    """
    boolean : expComp
            | expSubq
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_expBool_1(t):
    """
    expBool : expBool R_AND expBool
            | expBool R_OR expBool
    """
    t[0] = expression.BinaryLogicalOperation(t[1], t[3], t[2], t[1].row, t[1].column)
    repGrammar.append(t.slice)


def p_expBool_2(t):
    """
    expBool : R_NOT expBool
    """
    t[0] = expression.UnaryLogicalOperation(t[2], t[1], t[2].row, t[2].column)
    repGrammar.append(t.slice)


def p_expBool_3(t):
    """
    expBool : S_PARIZQ expBool S_PARDER
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_expBool_4(t):
    """
    expBool : boolean
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_expBool_5(t):
    """
    expBool : expBool optBoolPredicate
    """
    t[0] = expression.UnaryLogicalOperation(t[1], t[2], t[1].row, t[1].column)
    repGrammar.append(t.slice)


def p_optBoolPredicate_1(t):
    """
    optBoolPredicate : R_IS R_TRUE
    | R_IS R_FALSE
    | R_IS R_UNKNOWN
    """
    t[0] = t[1] + t[2]
    repGrammar.append(t.slice)


def p_optBoolPredicate_2(t):
    """
    optBoolPredicate : R_IS R_NOT R_TRUE
    | R_IS R_NOT R_FALSE
    | R_IS R_NOT R_UNKNOWN
    """
    t[0] = t[1] + t[2] + t[3]
    repGrammar.append(t.slice)


def p_columnName_id(t):
    """
    columnName : ID
    """
    t[0] = expression.Identifiers(None, t[1], t.slice[1].lineno, t.slice[1].lexpos)

    repGrammar.append(t.slice)


def p_columnName_table_id(t):
    """
    columnName : ID S_PUNTO ID
    """
    t[0] = expression.Identifiers(t[1], t[3], t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


# En caso de errores descomentar este metodo
'''
def p_columnName_table_idAll(t):
    """
    columnName : ID S_PUNTO O_PRODUCTO
    """
    t[0] = expression.TableAll(t[1], t.slice[1].lineno, t.slice[1].lexpos)
'''


def p_booleanCheck_1(t):
    """
    booleanCheck : idOrLiteral OL_MENORQUE idOrLiteral
    | idOrLiteral OL_MAYORQUE idOrLiteral
    | idOrLiteral OL_MAYORIGUALQUE idOrLiteral
    | idOrLiteral OL_MENORIGUALQUE idOrLiteral
    | idOrLiteral S_IGUAL idOrLiteral
    | idOrLiteral OL_DISTINTODE idOrLiteral
    """

    # t[0] = instruction.CheckOperation(t[1], t[3], t[2], t[1].row, t[1].column)
    t[0] = [t[1].value, t[3].value, t[2], t[1].type, t[3].type]
    repGrammar.append(t.slice)


def p_booleanCheck_2(t):
    """
    booleanCheck : idOrLiteral R_IS R_DISTINCT R_FROM idOrLiteral
    """

    t[0] = instruction.CheckOperation(
        t[1], t[5], t[2] + t[3] + t[4], t[1].row, t[1].column
    )
    t[0].execute(0)
    repGrammar.append(t.slice)


def p_booleanCheck_3(t):
    """
    booleanCheck : idOrLiteral R_IS R_NOT R_DISTINCT R_FROM idOrLiteral
    """

    t[0] = expression.CheckOperation(
        t[1], t[6], t[2] + t[3] + t[4] + t[5], t[1].row, t[1].column
    )
    repGrammar.append(t.slice)


def p_idOrLiteral(t):
    """
    idOrLiteral : ID
    | INTEGER
    | STRING
    | DECIMAL
    | CHARACTER
    | R_TRUE
    | R_FALSE
    """

    if t.slice[1].type == "CHARACTER" or t.slice[1].type == "STRING":
        tipo = "STRING"
    elif t.slice[1].type == "R_TRUE" or t.slice[1].type == "R_FALSE":
        t.slice[1].value = t.slice[1].value == "TRUE"
        tipo = "BOOLEAN"
    elif t.slice[1].type == "INTEGER" or t.slice[1].type == "DECIMAL":
        tipo = "NUMBER"
    else:
        tipo = "ID"

    t[0] = expression.CheckValue(
        t.slice[1].value, tipo, t.slice[1].lineno, t.slice[1].lexpos
    )

    t[0].execute(0)

    repGrammar.append(t.slice)


# endregion

# Statement para el ALTER
# region ALTER


def p_alterStmt(t):
    """alterStmt : R_ALTER R_DATABASE idOrString alterDb
    | R_ALTER R_TABLE idOrString alterTableList
    """
    if t[2] == "DATABASE":
        t[0] = instruction.AlterDataBase(t[4][0], t[3], t[4][1])
    repGrammar.append(t.slice)


def p_alterDb(t):
    """alterDb : R_RENAME R_TO idOrString
    | R_OWNER R_TO ownerOPts
    """
    t[0] = [t[1], t[3]]

    repGrammar.append(t.slice)


def p_ownerOpts(t):
    """
    ownerOPts : idOrString
    | R_CURRENT_USER
    | R_SESSION_USER
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_alterTableList(t):
    """
    alterTableList : alterTableList S_COMA alterTable
    | alterTable
    """
    repGrammar.append(t.slice)


def p_alterTable(t):
    """
    alterTable : R_ADD alterConstraint
    | alterCol
    | R_DROP R_CONSTRAINT ID
    | R_DROP R_COLUMN ID
    | R_RENAME R_COLUMN ID R_TO ID
    """
    repGrammar.append(t.slice)


def p_alterConstraint(t):
    """
    alterConstraint : R_CHECK S_PARIZQ booleanCheck S_PARDER
    | R_CONSTRAINT ID R_UNIQUE S_PARIZQ ID S_PARDER
    | createForeign
    | R_COLUMN ID types
    """
    repGrammar.append(t.slice)


def p_alterCol(t):
    """
    alterCol : R_ALTER R_COLUMN ID R_SET R_NOT R_NULL
    | R_ALTER R_COLUMN ID R_SET R_NULL
    | R_ALTER R_COLUMN ID R_TYPE types
    """
    repGrammar.append(t.slice)


# endregion


"""
Statement para el DROP
"""

# region DROP


def p_dropStmt(t):
    """
    dropStmt : R_DROP R_TABLE ifExists idOrString
    | R_DROP R_DATABASE ifExists idOrString
    """
    exists = True
    if t[3] == None:
        exists = False
    t[0] = instruction.Drop(t[2], t[4], exists)
    repGrammar.append(t.slice)


def p_ifExists(t):
    """ifExists : R_IF R_EXISTS
    |
    """

    repGrammar.append(t.slice)


# endregion

# Statement para el SELECT
# region SELECT


def p_selectStmt_1(t):
    """selectStmt : R_SELECT R_DISTINCT selectParams R_FROM tableExp whereCl groupByCl limitCl
    | selectStmt R_UNION allOpt selectStmt
    | selectStmt R_INTERSECT allOpt selectStmt
    | selectStmt R_EXCEPT allOpt selectStmt
    | S_PARIZQ selectStmt S_PARDER
    """
    repGrammar.append(t.slice)


# TODO: Cambiar gramatica | R_SELECT selectParams R_FROM tableExp joinList whereCl groupByCl orderByCl limitCl
# TODO: Cambiar gramatica | R_SELECT selectParams R_FROM tableExp joinList whereCl groupByCl orderByCl limitCl
def p_selectStmt_2(t):
    """selectStmt : R_SELECT selectParams fromCl whereCl groupByCl"""
    t[0] = instruction.Select(
        t[2].params, t[3], t[4], t[5][0], t[5][1], t.slice[1].lineno, t.slice[1].lexpos
    )
    repGrammar.append(t.slice)


def p_fromClause(t):
    """
    fromCl : R_FROM tableExp
    """
    tables = []
    aliases = []
    for i in range(len(t[2])):
        tables.append(t[2][i][0])
        aliases.append(t[2][i][1])
    t[0] = instruction.FromClause(tables, aliases, t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


def p_selectstmt_only_params(t):
    """selectStmt : R_SELECT selectParams"""
    t[0] = instruction.SelectOnlyParams(
        t[2].params, t[2].params[0].row, t[2].params[0].row
    )

    repGrammar.append(t.slice)


def p_allOpt(t):
    """allOpt : R_ALL
    |
    """

    repGrammar.append(t.slice)


def p_selectparams_all(t):
    """selectParams : O_PRODUCTO"""
    t[0] = instruction.SelectParams([], t.slice[1].lineno, t.slice[1].lexpos)

    repGrammar.append(t.slice)


def p_selectparams_params(t):
    """selectParams : selectList"""
    t[0] = instruction.SelectParams(t[1], t[1][0].row, t[1][0].column)

    repGrammar.append(t.slice)


# En caso de errores cambiar selectListParams -> expresion
def p_selectList_list(t):
    """selectList : selectList S_COMA selectListParams optAlias"""
    if t[4] != None:
        t[3].temp = t[4]
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)


# En caso de errores cambiar selectListParams -> expresion
def p_selectList_u(t):
    """selectList : selectListParams optAlias"""
    if t[2] != None:
        t[1].temp = t[2]
    t[0] = [t[1]]

    repGrammar.append(t.slice)


def p_selectListParams_1(t):
    """selectListParams : expresion"""
    t[0] = t[1]

    repGrammar.append(t.slice)


def p_selectListParams_2(t):
    """selectListParams : ID S_PUNTO O_PRODUCTO"""
    t[0] = expression.TableAll(t[1], t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


def p_optalias_as(t):
    """
    optAlias : R_AS idOrString
    """
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_optalias_id(t):
    """
    optAlias : idOrString
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_optalias_none(t):
    """optAlias : """
    t[0] = None
    repGrammar.append(t.slice)


def p_tableexp_list(t):
    """tableExp : tableExp S_COMA fromBody """
    t[1].append(t[3])
    t[0] = t[1]

    repGrammar.append(t.slice)


def p_tableexp_u(t):
    """tableExp : fromBody """
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_fromBody(t):
    """fromBody : ID optAlias"""
    if t[2] != None:
        t[0] = [instruction.TableID(t[1], t.slice[1].lineno, t.slice[1].lexpos), t[2]]
    else:
        t[0] = [instruction.TableID(t[1], t.slice[1].lineno, t.slice[1].lexpos), ""]
    repGrammar.append(t.slice)


def p_tableexp_subq(t):
    """fromBody : S_PARIZQ selectStmt S_PARDER R_AS idOrString"""
    t[0] = [t[2], t[5]]

    repGrammar.append(t.slice)


def p_joinList(t):
    """joinList : joinList2
    |
    """

    repGrammar.append(t.slice)


def p_joinList2(t):
    """joinList2 : joinList2 joinCl
    | joinCl"""
    repGrammar.append(t.slice)


def p_joinCl(t):
    """joinCl : joinOpt R_JOIN columnName R_ON expBool
    | joinOpt R_JOIN columnName R_USING S_PARIZQ nameList S_PARDER
    | R_NATURAL joinOpt R_JOIN columnName
    """

    repGrammar.append(t.slice)


def p_nameList(t):
    """nameList : nameList S_COMA columnName
    | columnName
    """
    repGrammar.append(t.slice)


def p_joinOpt(t):
    """joinOpt : R_INNER
    | R_LEFT
    | R_LEFT R_OUTER
    | R_RIGHT
    | R_RIGHT R_OUTER
    | R_FULL
    | R_FULL R_OUTER
    """
    repGrammar.append(t.slice)


def p_whereCl(t):
    """whereCl : R_WHERE expBool"""
    if t[2] != None:
        t[0] = instruction.WhereClause(t[2], t.slice[1].lineno, t.slice[1].lexpos)
    else:
        t[0] = None
    repGrammar.append(t.slice)


def p_whereCl_none(t):
    """whereCl : """
    t[0] = None

    repGrammar.append(t.slice)



def p_groupByCl_1(t):
    """
    groupByCl : R_GROUP R_BY groupList havingCl
    """
    t[0] = [t[3], t[4]]
    repGrammar.append(t.slice)

def p_groupByCl_2(t):
    """
    groupByCl : 
    """
    t[0] = [None, None]
    

def p_groupList_1(t):
    """
    groupList :  groupList S_COMA columnName
            | groupList S_COMA INTEGER
    """
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)

def p_groupList_2(t):
    """
    groupList :  columnName
            | INTEGER
    """
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_havingCl(t):
    """havingCl : R_HAVING expBool
    """
    t[0] = t[2]
    repGrammar.append(t.slice)

def p_havingCl(t):
    """havingCl :
    """
    t[0] = None
    


def p_orderByCl(t):
    """orderByCl : R_ORDER R_BY orderList
    |
    """

    repGrammar.append(t.slice)


def p_orderList(t):
    """orderList : orderList S_COMA orderByElem
    | orderByElem
    """
    repGrammar.append(t.slice)


def p_orderByElem(t):
    """orderByElem : columnName orderOpts orderNull"""
    repGrammar.append(t.slice)


def p_orderOpts(t):
    """orderOpts : R_ASC
    | R_DESC
    |
    """
    repGrammar.append(t.slice)


def p_orderNull(t):
    """orderNull : R_NULL R_FIRST
    | R_NULL R_LAST
    |
    """
    repGrammar.append(t.slice)


def p_limitCl(t):
    """limitCl : R_LIMIT INTEGER offsetLimit
    | R_LIMIT R_ALL offsetLimit
    |
    """
    repGrammar.append(t.slice)


def p_offsetLimit(t):
    """offsetLimit : R_OFFSET INTEGER
    |
    """
    repGrammar.append(t.slice)


# endregion

# Statement para el INSERT

# region INSERT


def p_insertStmt(t):
    """insertStmt : R_INSERT R_INTO ID paramsColumn R_VALUES S_PARIZQ paramsList S_PARDER"""

    t[0] = instruction.InsertInto(t[3], t[4], t[7])
    repGrammar.append(t.slice)


def p_paramsColumn(t):
    """paramsColumn : S_PARIZQ idList S_PARDER"""
    t[0] = t[2]
    repGrammar.append(t.slice)


def p_paramsColumn_none(t):
    """paramsColumn :"""
    t[0] = None

    repGrammar.append(t.slice)


# endregion

# Statement para el UPDATE

# region UPDATE


def p_updateStmt(t):
    """updateStmt : R_UPDATE fromBody R_SET updateCols whereCl"""
    fc = instruction.FromClause(
        [t[2][0]], [t[2][1]], t.slice[1].lineno, t.slice[1].lexpos
    )
    t[0] = instruction.Update(fc, t[4], t[5], t.slice[1].lineno, t.slice[1].lexpos)

    repGrammar.append(t.slice)


def p_updateCols_list(t):
    """updateCols : updateCols S_COMA updateVals"""
    t[1].append(t[3])
    t[0] = t[1]
    repGrammar.append(t.slice)


def p_updateCols_u(t):
    """updateCols : updateVals """
    t[0] = [t[1]]
    repGrammar.append(t.slice)


def p_updateVals(t):
    """updateVals : ID S_IGUAL updateExp"""
    t[0] = instruction.Assignment(t[1], t[3], t.slice[1].lineno, t.slice[1].lexpos)

    repGrammar.append(t.slice)


def p_updateExp(t):
    """updateExp : datatype
    | R_DEFAULT
    """
    t[0] = t[1]
    repGrammar.append(t.slice)


# endregion

# Statement para el DELETE y OTROS

# region DELETE, ETC


def p_deleteStmt(t):
    """deleteStmt : R_DELETE fromCl whereCl"""
    t[0] = instruction.Delete(t[2], t[3], t.slice[1].lineno, t.slice[1].lexpos)
    repGrammar.append(t.slice)


def p_truncateStmt(t):
    """truncateStmt : R_TRUNCATE tableOpt ID"""
    t[0] = instruction.Truncate(t[3])
    repGrammar.append(t.slice)


def p_tableOpt(t):
    """tableOpt : R_TABLE
    |
    """
    repGrammar.append(t.slice)


def p_showStmt(t):
    """showStmt : R_SHOW R_DATABASES likeOpt"""

    t[0] = instruction.showDataBases(t[3])
    repGrammar.append(t.slice)


def p_likeOpt(t):
    """likeOpt : R_LIKE STRING
    |
    """
    if len(t) == 3:
        t[0] = t[2]
    else:
        t[0] = None
    repGrammar.append(t.slice)


def p_useStmt(t):
    """useStmt : R_USE ID"""
    t[0] = instruction.useDataBase(t[2])

    repGrammar.append(t.slice)


# endregion


listErrors = list()
PostgreSQL = list()


def p_error(t):
    try:
        print(t)
        print("Error sintáctico en '%s'" % t.value)
        listErrors.insert(
            len(listErrors), ["Error sintáctico en '%s'" % t.value, t.lineno]
        )
        PostgreSQL.insert(
            len(PostgreSQL), "ERROR: 42601: error de sintaxis en '%s'" % t.value
        )
    except AttributeError:
        print("end of file")


parser = yacc.yacc()


def returnSintacticErrors():
    return listErrors


def returnPostgreSQLErrors():
    expression.list_errors += PostgreSQL
    instruction.sintaxPostgreSQL += expression.list_errors
    return instruction.sintaxPostgreSQL


def returnSemanticErrors():
    return instruction.semanticErrors


def getRepGrammar():
    return repGrammar


def parse(input):
    try:
        global listErrors, PostgreSQL
        listErrors = list()
        PostgreSQL = list()
        expression.list_errors = list()
        instruction.sintaxPostgreSQL = list()
        instruction.semanticErrors = list()
        lexer.lineno = 1
        result = parser.parse(input)
        return result
    except Exception as e:
        print(e)
        return None
