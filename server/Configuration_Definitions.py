
class Configuration_Definitions(object):

    PLL_freq =  100.0e6

    trigger_type_str =      ['Auto','Normal','Single']

    voltage_scales_int = [
            50  , 20    , 10    ,
            5   , 2     , 1     ,
            0.5 , 0.2   , 0.1   ]

    voltage_scales_str = [
            "5 V/div"    , "2 V/div"     , "1 V/div"     ,
            "500 mV/div" , "200 mV/div"  , "100 mV/div"  ,
            "50 mV/div"  , "20 mV/div"   , "10 mV/div"   ]

# https://docs.google.com/spreadsheets/d/1bY0WnD-5lPMWCzxdtq6AacOtwHaX9ymvFMviB-GncO8/edit#gid=2102131143
    Att_Sel = [
            1   , 1     , 1     ,
            0   , 0     , 0     ,
            0   , 0     , 0     ]

    Gain_Sel = [
            0   , 1     , 2     ,
            0   , 1     , 2     ,
            3   , 4     , 5     ]

    timebase_scales_int =   [
            1       , 0.5       , 0.2       , # 1    s/div
            0.1     , 0.05      , 0.02      , # 100 ms/div
            0.01    , 0.005     , 0.002     , # 10  ms/div
            0.001   , 0.0005    , 0.0002    , # 1   ms/div
            0.0001  , 0.00005   , 0.00002   , # 100 us/div
            0.00001 , 0.000005  , 0.000002  , # 10  us/div
            0.000001, 0.0000005 , 0.0000002 , # 1   us/div
            0.0000001 ]            # 100 ns/div

    timebase_scales_str =   [
            "1 s"       , "500 ms"  , "200 ms"  ,
            "100 ms"    , "50 ms"   , "20 ms"   ,
            "10 ms"     , "5 ms"    , "2 ms"    ,
            "1 ms"      , "500 us"  , "200 us"  ,
            "100 us"    , "50 us"   , "20 us"   ,
            "10 us"     , "5 us"    , "2 us"    ,
            "1 us"      , "500 ns"  , "200 ns"  ,
            "100 ns" ]

# https://docs.google.com/spreadsheets/d/1bY0WnD-5lPMWCzxdtq6AacOtwHaX9ymvFMviB-GncO8/edit#gid=80072049
# Values updated 28/02/2018 - 00:59hs
        # Clock_Adc_Div_Sel = [
        #         30520   , 15260 , 6104  ,
        #         3052    , 1526  , 612   ,
        #         306     , 154   , 64    ,
        #         32      , 32    , 26    ,
        #         26      , 26    , 10    ,
        #         6       , 6     , 6     ,
        #         6       , 4     , 4     ,
        #         4 ]
        #
        # Mov_Ave_Sel = [
        #         16      , 16    , 16    ,
        #         16      , 16    , 16    ,
        #         16      , 16    , 16    ,
        #         16      , 8     , 4     ,
        #         2       , 1     , 1     ,
        #         1       , 1     , 1     ,
        #         1       , 1     , 1     ,
        #         1 ]
        #
        # #Num_Samples = list(reversed(Num_Samples))
        # Num_Samples = list(reversed(
        #         [25      , 50    , 125   ,
        #         167     , 334   , 834   ,
        #         1667    , 2000  , 1924  ,
        #         1924    , 1924  , 1954  ,
        #         1954    , 1954  , 2030  ,
        #         2043    , 2043  , 2048  ,
        #         2048    , 2048  , 2048  ,
        #         2048 ]
        #         ))


    Clock_Adc_Div_Sel = [
            30520,15260,6104,
            3052,1526,612,
            306,154,64,
            32,32,12,
            6,6,6,
            6,4,4,
            4,4,4,
            4 ]

    Mov_Ave_Sel = [
            16,16,16,
            16,16,16,
            16,16,16,
            16,16,16,
            16,8,8,
            4,4,4,
            2,1,1,
            1 ]

    Num_Samples = [
        2048,2048,2048,
        2048,2048,2043,
        2043,2030,1954,
        1954,977,1042,
        1042,1042,417,
        417,313,125,
        125,125,50,
        25
    ]
