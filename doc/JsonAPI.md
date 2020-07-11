# The JSON format used to describe MSOL visualization on tree decompositions

Short version. For the full schema see the *TDVisu.schema.json*!

```perl
{
    "treeDecJson" : 
    {
        "bagpre" : STR,
        "num_vars" : INT,
        Optional("joinpre" : STR, default= "Join %d~%d"),
        Optional("solpre" : STR, default= "sol%d"),
        Optional("soljoinpre" : STR, default= "solJoin%d~%d"),
        
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

    Optional("incidenceGraph" : Dict or List of
    {
        Optional("subgraph_name_one" : STR, default="clauses"),
        Optional("subgraph_name_two" : STR, default="variables"),

        Optional("var_name_one" : STR, default=""),
        Optional("var_name_two" : STR, default=""),

        Optional("infer_primal" : BOOLEAN, default=false),
        Optional("infer_dual" : BOOLEAN, default=false),
        Optional("primal_file": STR, default="PrimalGraphStep"),
        Optional("inc_file": STR, default="IncidenceGraphStep"),
        Optional("dual_file": STR, default="DualGraphStep"),
        Optional("fontsize" : INT, default=16),
        Optional("penwidth": FLOAT, default=2.2),
        Optional("second_shape" : STR, default="diamond"),
        Optional("column_distance" : FLOAT, default=0.5),
        
        "edges" : [
            {"id" : INT (subgraphOneId), 
            "list" : [INT...]
            }
            ...
        ]
    }),

    Optional("generalGraph" : Dict or List of
    {
        Optional("extra_nodes" : Optional[list] = null),
        Optional("graph_name" : STR, default="graph"),
        Optional("file_basename" : STR, default="graph"),
        Optional("var_name" : STR, default=""),
        Optional("do_sort_nodes" : BOOLEAN, default=false),
        Optional("do_adj_nodes" : LIST, default=[]),
        Optional("fontsize" : INT, default=20),
        Optional("first_color" : STR/COLOR, default ="yellow"),
        Optional("first_style" : STR, default ="filled"),
        Optional("second_color" : STR/COLOR, default="green"),
        Optional("second_style" : STR, default="dotted,filled"),
        Optional("third_color" : STR, default="red"),
        
        "edges" : [
            [INT, INT],
            ...
        ]
    }),

    Optional("td_file": STR, default="TDStep"),
    Optional("colors": List, default=[
                "#0073a1",
                "#b14923",
                "#244320",
                "#b1740f",
                "#a682ff",
                "#004066",
                "#0d1321",
                "#da1167",
                "#604909",
                "#0073a1",
                "#b14923",
                "#244320",
                "#b1740f",
                "#a682ff"]),
    Optional("orientation" : Any["BT", "TB", "LR", "RL"] , default="BT"),
    Optional("linesmax" : INT, default=100),
    Optional("columnsmax" : INT, default=20),
    Optional("bagcolor" : STR, default="white"),
    Optional("fontsize" : INT, default=20),
    Optional("penwidth" : FLOAT, default=2.2),
    Optional("fontcolor" : STR, default="black"),
    
    Optional("emphasis" : DICT, default=
        {
            "firstcolor" : STR/COLOR, default="yellow",
            "secondcolor" : STR/COLOR, default="green",
            "firststyle" : STR, default="filled",
            "secondstyle" : STR, default="dotted,filled"
        }
    )
    
    Optional("svgjoin" :
        {
            "base_names" : [STR],
            Optional("folder" : STR/NULL, default=null),
            Optional("outname" : STR, default="combined"),
            Optional("suffix" : STR, default="%d.svg"),
            Optional("preserve_aspectratio" : STR, default="xMinYMin"),
            Optional("num_images" : INT, default=1),
            Optional("padding" : [INT], default=0),
            Optional("scale2" : [FLOAT], default=1),
            Optional("v_top" : [FLOAT/STR], default="top"),
            Optional("v_bottom" : [FLOAT/STR]/NULL, default=null),
        }
    )
}
