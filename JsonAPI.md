# The JSON format used to describe MSOL visualization on tree decompositions


```perl
{
    "incidenceGraph" : false or
    {
        Optional("subgraphNameOne" : STR, default='clauses'),
        Optional("subgraphNameTwo" : STR, default='variables'),

        Optional("varNameOne" : STR, default=''),
        Optional("varNameTwo" : STR, default=''),

        Optional("inferPrimal" : BOOLEAN, default=false),
        Optional("inferDual" : BOOLEAN, default=false),
        Optional("fontsize" : INT, default=16),
        Optional("secondshape" : STR, default='diamond'),
        Optional("columnDistance" : FLOAT, default=0.5),
        
        "edges" : [
            {"id" : INT (subgraphOneId), 
            "list" : [INT...]
            }
            ...
        ]
    },

    "generalGraph" : false or
    {
        Optional("graphName" : STR, default='graph'),
        Optional("varName" : STR, default=''),
        Optional("sortNodes" : BOOLEAN, default=false),
        Optional("needAdjNodes" : BOOLEAN, default=false),
        Optional("extraNodes" : LIST, default=[]),
        Optional("fontsize" : INT, default=20),
        Optional("firstColor" : STR/COLOR, default ='yellow'),
        Optional("firstStyle" : STR, default ='filled'),
        Optional("secondColor : STR/COLOR, default='green'),
        Optional("secondStyle : STR, default='dotted,filled'),
        
        "edges" : [
            [INT, INT],
            ...
        ]
    },

    "tdTimeline" : 
    [
        [INT (bagId)] or 
        [INT (bagId) or [INT(bagId), INT(bagId)], 
            [[
                [(firstrow)...],
                [(secondrow)...],
                ...
            ]
            ,STR (header)
            ,STR (footer)
            ,BOOL (transpose)
            ]
        ]
        ...
    ],

    "treeDecJson" : 
    {
        "bagpre" : STR,
        "numVars" : INT,
        Optional("joinpre" : STR, default= 'Join %d~%d'),
        Optional("solpre" : STR, default= 'sol%d'),
        Optional("soljoinpre" : STR, default= 'solJoin%d~%d'),
        
        "edgearray" : 
            [[INT, INT]...],
        "labeldict" : 
            [
                {
                    "id" : INT (bagId),
                    "items" : [ INT... ],
                    "labels" : [ STR... ]
                }
                ...
            ],
    },
    
    Optional("orientation" : Any['BT', 'TB', 'LR', 'RL'] , default='BT'),
    Optional("linesmax" : INT, default=100),
    Optional("columnsmax" : INT, default=20),
    Optional("bagcolor" : STR, default='white'),
    Optional("fontsize" : INT, default=20),
    Optional("penwidth" : FLOAT, default=2.2),
    Optional("fontcolor" : STR, default='black'),
    
    Optional("emphasis" : DICT, default=
        {
            "firstcolor" : STR/COLOR, default='yellow',
            "secondcolor" : STR/COLOR, default='green',
            "firststyle" : STR, default='filled',
            "secondstyle" : STR, default='dotted,filled'
        }
    )
    
    Optional("svgjoin" :
        {
            "base_names" : [STR],
            Optional("folder" : STR/NULL, default=null),
            Optional("outname" : STR, default='combined'),
            Optional("suffix" : STR, default='%d.svg'),
            Optional("preserve_aspectratio" : STR, default='xMinYMin'),
            Optional("numimages" : INT, default=1),
            Optional("padding" : [INT], default=0),
            Optional("scale2" : [FLOAT], default=1),
            Optional("v_top" : [FLOAT/STR], default='top'),
            Optional("v_bottom" : [FLOAT/STR]/NULL, default=null),
        }
    )
}
