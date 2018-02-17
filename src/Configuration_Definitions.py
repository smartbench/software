
class Configuration_Definitions(object):

    voltage_scales_int =    [   50  , 20    , 10    ,
                                5   , 2     , 1     ,
                                0.5 , 0.2   , 0.1   ]

    voltage_scales_str =    [   "5 V/div"    , "2 V/div"     , "1 V/div"     ,
                                "500 mV/div" , "200 mV/div"  , "100 mV/div"  ,
                                "50 mV/div"  , "20 mV/div"   , "10 mV/div"   ]

    timebase_scales_int =   [   10      , 5         , 2         , # 10   s
                                1       , 0.5       , 0.2       , # 1    s
                                0.1     , 0.05      , 0.02      , # 100 ms
                                0.01    , 0.005     , 0.002     , # 10  ms
                                0.001   , 0.0005    , 0.0002    , # 1   ms
                                0.0001  , 0.00005   , 0.00002   , # 100 us
                                0.00001 , 0.000005  , 0.000002  , # 10  us
                                0.000001, 0.0000005 ]             # 1   us

    timebase_scales_str =   [   "10 s"      , "5 s"     , "2 s"     ,
                                "1 s"       , "500 ms"  , "200 ms"  ,
                                "100 ms"    , "50 ms"   , "20 ms"   ,
                                "10 ms"     , "5 ms"    , "2 ms"    ,
                                "1 ms"      , "500 us"  , "200 us"  ,
                                "100 us"    , "50 us"   , "20 us"   ,
                                "10 us"     , "5 us"    , "2 us"    ,
                                "1 us"      , "500 ns" ]

# https://docs.google.com/spreadsheets/d/1bY0WnD-5lPMWCzxdtq6AacOtwHaX9ymvFMviB-GncO8/edit#gid=2102131143
    Att_Sel =               [   1   , 1     , 1     ,
                                0   , 0     , 0     ,
                                0   , 0     , 0     ]

    Gain_Sel =              [   0   , 1     , 2     ,
                                0   , 1     , 2     ,
                                3   , 4     , 5     ]

# https://docs.google.com/spreadsheets/d/1bY0WnD-5lPMWCzxdtq6AacOtwHaX9ymvFMviB-GncO8/edit#gid=80072049

    PLL_freq =  100.0e6

    Clock_Adc_Div_Sel =     [   3814    , 1908  , 763   ,
                                382     , 191   , 77    ,
                                39      , 20    , 8     ,
                                5       , 5     , 5     ,
                                5       , 5     , 5     ,
                                5       , 5     , 5     ,
                                5       , 5     , 5     ,
                                5       ]

    Mov_Ave_Sel =           [   16      , 16    , 16    ,
                                16      , 16    , 16    ,
                                16      , 16    , 16    ,
                                16      , 8     , 4     ,
                                2       , 1     , 1     ,
                                1       , 1     , 1     ,
                                1       , 1     , 1     ,
                                1       ]
