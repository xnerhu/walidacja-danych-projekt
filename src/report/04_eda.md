# Eksploracyjna analiza danych (EDA)

*Generated: 2026-01-18 19:02*


---

## Wprowadzenie

Niniejszy raport przedstawia eksploracyjna analize danych (EDA) polaczonego zbioru danych dotyczacego emisji CO2, zuzycia energii i rozwoju gospodarczego krajow swiata.

| Metric            | Value     |
|:------------------|:----------|
| Liczba obserwacji | 4,557     |
| Liczba zmiennych  | 128       |
| Liczba krajow     | 216       |
| Zakres czasowy    | 2000-2020 |


---

## Statystyki opisowe

Ponizej przedstawiono statystyki opisowe dla kluczowych zmiennych numerycznych.

### Kluczowe zmienne

| variable                   |   count |          mean |            std |           min |       median |             max |
|:---------------------------|--------:|--------------:|---------------:|--------------:|-------------:|----------------:|
| population                 |    4536 |   3.24976e+07 |    1.29247e+08 | 536           |  5.85172e+06 |     1.42611e+09 |
| gdp                        |    3444 |   5.51694e+11 |    1.83062e+12 |   3.12854e+08 |  7.32618e+10 |     2.41518e+13 |
| co2                        |    4494 | 146.11        |  708.27        |   0           |  7.58        | 10896.5         |
| co2_per_capita             |    4473 |   5.1         |    6.66        |   0.02        |  2.83        |    67.73        |
| primary_energy_consumption |    4257 | 684.07        | 2891.27        |   0           | 42.74        | 41493.9         |

### Pelna tabela statystyk

<details>
<summary>Pokaz wszystkie zmienne</summary>

| variable                                                     |   count |   missing |   missing_pct |             mean |              std |              min |              q25 |           median |              q75 |              max |   skewness |   kurtosis |
|:-------------------------------------------------------------|--------:|----------:|--------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------:|-----------:|
| year                                                         |    4557 |         0 |          0    |   2010           |      6.056       |   2000           |   2005           |   2010           |   2015           |   2020           |     0      |    -1.2055 |
| population                                                   |    4536 |        21 |          0.46 |      3.24976e+07 |      1.29247e+08 |    536           | 686188           |      5.85172e+06 |      2.1232e+07  |      1.42611e+09 |     8.9059 |    84.8241 |
| gdp                                                          |    3444 |      1113 |         24.42 |      5.51694e+11 |      1.83062e+12 |      3.12854e+08 |      2.24843e+10 |      7.32618e+10 |      3.46355e+11 |      2.41518e+13 |     7.54   |    66.9516 |
| cement_co2                                                   |    4365 |       192 |          4.21 |      5.8551      |     42.5665      |      0           |      0           |      0.366       |      1.858       |    828.71        |    15.1104 |   245.065  |
| cement_co2_per_capita                                        |    4344 |       213 |          4.67 |      0.111       |      0.167       |      0           |      0           |      0.05        |      0.154       |      1.457       |     2.743  |    10.109  |
| co2                                                          |    4494 |        63 |          1.38 |    146.106       |    708.272       |      0           |      1.0158      |      7.5835      |     55.5712      |  10896.5         |    10.1516 |   117.885  |
| co2_growth_abs                                               |    4494 |        63 |          1.38 |      2.2799      |     34.9208      |   -545.958       |     -0.1178      |      0.026       |      0.7268      |    910.106       |    12.2698 |   289.343  |
| co2_growth_prct                                              |    4473 |        84 |          1.84 |      2.9786      |     13.043       |    -51.055       |     -2.459       |      1.783       |      7.143       |    193.665       |     3.4289 |    36.6828 |
| co2_including_luc                                            |    4074 |       483 |         10.6  |    193.741       |    770.118       |    -18.087       |      5.407       |     30.3115      |     93.205       |  10632.8         |     8.8072 |    90.7014 |
| co2_including_luc_growth_abs                                 |    4074 |       483 |         10.6  |      1.9918      |     54.1061      |   -921.548       |     -1.9108      |      0           |      2.027       |    993.495       |     3.4532 |   119.526  |
| co2_including_luc_growth_prct                                |    4074 |       483 |         10.6  |     -2.4279      |    248.544       | -11927.2         |     -7.5418      |      0           |      7.2438      |   3073.51        |   -38.4319 |  1737.4    |
| co2_including_luc_per_capita                                 |    4074 |       483 |         10.6  |      5.9568      |      6.6512      |     -4.493       |      1.726       |      4.048       |      7.943       |     67.744       |     2.9004 |    13.8591 |
| co2_including_luc_per_gdp                                    |    3402 |      1155 |         25.35 |      0.785       |      1.5492      |     -0.293       |      0.233       |      0.37        |      0.69        |     21.064       |     6.9611 |    64.5628 |
| co2_including_luc_per_unit_energy                            |    3942 |       615 |         13.5  |      1.2203      |      3.4842      |     -1.787       |      0.191       |      0.256       |      0.761       |     58.584       |     8.6655 |   102.526  |
| co2_per_capita                                               |    4473 |        84 |          1.84 |      5.1033      |      6.6623      |      0.021       |      0.775       |      2.83        |      6.97        |     67.727       |     3.0327 |    14.3522 |
| co2_per_gdp                                                  |    3444 |      1113 |         24.42 |      0.2862      |      0.2223      |      0.028       |      0.149       |      0.23        |      0.348       |      2.151       |     2.6538 |    10.9262 |
| co2_per_unit_energy                                          |    4236 |       321 |          7.04 |      0.2213      |      0.0933      |      0.035       |      0.18        |      0.213       |      0.245       |      1.695       |     4.3617 |    37.1757 |
| coal_co2                                                     |    2874 |      1683 |         36.93 |     94.7576      |    549.482       |      0           |      0.158       |      2.1425      |     24.986       |   7679.38        |    10.8    |   128.985  |
| coal_co2_per_capita                                          |    2874 |      1683 |         36.93 |      1.3053      |      2.1081      |      0           |      0.012       |      0.267       |      1.851       |     13.953       |     2.2446 |     5.2863 |
| consumption_co2                                              |    2514 |      2043 |         44.83 |    253.703       |    870.288       |      0.17        |      9.9268      |     42.234       |    165.667       |   9798.92        |     7.246  |    58.4704 |
| consumption_co2_per_capita                                   |    2514 |      2043 |         44.83 |      6.6815      |      7.0559      |      0.04        |      1.1425      |      4.392       |     10.1525      |     44.9         |     1.5929 |     2.839  |
| consumption_co2_per_gdp                                      |    2493 |      2064 |         45.29 |      0.3142      |      0.1608      |      0.003       |      0.201       |      0.281       |      0.408       |      1.299       |     1.1781 |     2.5097 |
| cumulative_cement_co2                                        |    4365 |       192 |          4.21 |    141.982       |    650.264       |      0           |      0           |     10.396       |     72.214       |  14487.4         |    13.5061 |   230.625  |
| cumulative_co2                                               |    4494 |        63 |          1.38 |   6180.85        |  29012.9         |      0.059       |     28.305       |    256.741       |   2231.42        | 414968           |     9.8386 |   112.749  |
| cumulative_co2_including_luc                                 |    4074 |       483 |         10.6  |  11262.8         |  42933.2         |    -37.442       |    289.703       |   1655.3         |   5363.37        | 540205           |     8.3479 |    82.3649 |
| cumulative_coal_co2                                          |    2874 |      1683 |         36.93 |   4727.58        |  18498.4         |      0           |      7.0848      |    116.442       |   1237.84        | 179172           |     6.5355 |    47.8557 |
| cumulative_flaring_co2                                       |    4494 |        63 |          1.38 |     68.9231      |    224.484       |      0           |      0           |      0           |     15.3875      |   2223.82        |     4.97   |    27.6754 |
| cumulative_gas_co2                                           |    2616 |      1941 |         42.59 |   1433.03        |   6080.82        |      0           |     15.9612      |    176.362       |    848.137       |  75673.5         |     8.8268 |    85.2404 |
| cumulative_luc_co2                                           |    4137 |       420 |          9.22 |   4936.64        |  15923.4         |  -3890.29        |     69.751       |    657.463       |   2996.34        | 125407           |     5.5352 |    32.3563 |
| cumulative_oil_co2                                           |    4471 |        86 |          1.89 |   2084.33        |   9912.12        |      0.059       |     23.9115      |    157.857       |   1127.39        | 156625           |    11.7203 |   155.266  |
| cumulative_other_co2                                         |     966 |      3591 |         78.8  |    198.149       |    703.266       |      0           |      8.0968      |     24.3565      |     79.8802      |   4884.2         |     4.8468 |    23.1767 |
| energy_per_capita                                            |    4257 |       300 |          6.58 |  25186.6         |  34278.8         |      0           |   3125.51        |  12044.5         |  34236.5         | 270981           |     2.6553 |     8.9175 |
| energy_per_gdp                                               |    3432 |      1125 |         24.69 |      1.3568      |      0.9702      |      0.078       |      0.749       |      1.1275      |      1.7238      |     10.141       |     2.5893 |    11.4203 |
| flaring_co2                                                  |    4494 |        63 |          1.38 |      1.6899      |      5.8745      |      0           |      0           |      0           |      0.521       |     84.52        |     6.3769 |    50.3618 |
| flaring_co2_per_capita                                       |    4473 |        84 |          1.84 |      0.1002      |      0.4074      |      0           |      0           |      0           |      0.034       |      9.772       |    11.1121 |   180.607  |
| gas_co2                                                      |    2616 |      1941 |         42.59 |     49.1664      |    144.738       |      0           |      1.084       |      8.1175      |     41.9488      |   1632.06        |     6.8671 |    54.925  |
| gas_co2_per_capita                                           |    2616 |      1941 |         42.59 |      2.1675      |      4.7636      |      0           |      0.0948      |      0.774       |      2.064       |     42.822       |     4.6577 |    25.343  |
| ghg_excluding_lucf_per_capita                                |    4146 |       411 |          9.02 |      5.9503      |      8.3616      |      0.129       |      1.0825      |      3.246       |      7.5043      |    105.445       |     4.2108 |    28.9474 |
| ghg_per_capita                                               |    4179 |       378 |          8.29 |      8.1876      |      8.6242      |     -0.018       |      2.9805      |      5.816       |     10.208       |    105.796       |     3.5803 |    22.4466 |
| land_use_change_co2                                          |    4137 |       420 |          9.22 |     33.7232      |    148.606       |   -263.683       |     -0.028       |      1.897       |     19.257       |   2998.52        |     9.4446 |   114.347  |
| land_use_change_co2_per_capita                               |    4074 |       483 |         10.6  |      1.3434      |      3.2603      |     -6.658       |     -0.024       |      0.2835      |      1.7565      |     50.522       |     3.5566 |    24.1578 |
| methane                                                      |    4179 |       378 |          8.29 |     41.585       |    124.958       |      0.001       |      1.835       |      9.762       |     27.7965      |   1398.96        |     6.6366 |    51.497  |
| methane_per_capita                                           |    4179 |       378 |          8.29 |      1.7464      |      2.6225      |      0.072       |      0.657       |      1.029       |      1.6375      |     42.768       |     5.8172 |    50.97   |
| nitrous_oxide                                                |    4221 |       336 |          7.37 |     13.0691      |     41.712       |      0           |      0.393       |      2.962       |      9.636       |    466.877       |     7.4645 |    64.6118 |
| nitrous_oxide_per_capita                                     |    4221 |       336 |          7.37 |      0.4859      |      0.5761      |      0           |      0.192       |      0.311       |      0.517       |      5.397       |     3.5858 |    16.406  |
| oil_co2                                                      |    4471 |        86 |          1.89 |     47.9428      |    190.45        |      0.004       |      0.806       |      4.338       |     24.348       |   2584.13        |     9.4292 |   104.418  |
| oil_co2_per_capita                                           |    4471 |        86 |          1.89 |      2.768       |      3.9917      |      0.013       |      0.4465      |      1.48        |      3.498       |     42.354       |     3.9832 |    23.6799 |
| other_co2_per_capita                                         |     966 |      3591 |         78.8  |      0.1029      |      0.0813      |      0           |      0.054       |      0.082       |      0.1358      |      0.563       |     2.1439 |     7.3464 |
| other_industry_co2                                           |     966 |      3591 |         78.8  |      8.4289      |     28.4244      |      0           |      0.3952      |      1.145       |      3.914       |    198.092       |     4.6609 |    20.9736 |
| primary_energy_consumption                                   |    4257 |       300 |          6.58 |    684.068       |   2891.27        |      0           |      6.569       |     42.744       |    318.558       |  41493.9         |     8.93   |    90.1596 |
| share_global_cement_co2                                      |    4365 |       192 |          4.21 |      0.481       |      3.2638      |      0           |      0           |      0.03        |      0.159       |     51.791       |    13.5951 |   193.136  |
| share_global_co2                                             |    4494 |        63 |          1.38 |      0.4524      |      2.1538      |      0           |      0.003       |      0.023       |      0.1758      |     30.993       |     9.6648 |   104.078  |
| share_global_co2_including_luc                               |    4074 |       483 |         10.6  |      0.5064      |      1.9886      |     -0.048       |      0.014       |      0.078       |      0.247       |     26.8         |     8.4802 |    82.3272 |
| share_global_coal_co2                                        |    2874 |      1683 |         36.93 |      0.7304      |      4.0628      |      0           |      0.001       |      0.017       |      0.18        |     53.826       |     9.9299 |   107.451  |
| share_global_cumulative_cement_co2                           |    4365 |       192 |          4.21 |      0.4811      |      1.9897      |      0           |      0           |      0.038       |      0.253       |     33.354       |    10.5762 |   137.764  |
| share_global_cumulative_co2                                  |    4494 |        63 |          1.38 |      0.4567      |      2.1351      |      0           |      0.002       |      0.0185      |      0.1698      |     28.954       |     9.8139 |   112.172  |
| share_global_cumulative_co2_including_luc                    |    4074 |       483 |         10.6  |      0.5168      |      1.9641      |     -0.002       |      0.013       |      0.077       |      0.247       |     23.537       |     8.3234 |    81.8768 |
| share_global_cumulative_coal_co2                             |    2874 |      1683 |         36.93 |      0.7304      |      2.8283      |      0           |      0.001       |      0.018       |      0.187       |     26.31        |     6.3785 |    45.4677 |
| share_global_cumulative_flaring_co2                          |    4494 |        63 |          1.38 |      0.4673      |      1.5108      |      0           |      0           |      0           |      0.103       |     12.012       |     4.8191 |    25.1418 |
| share_global_cumulative_gas_co2                              |    2616 |      1941 |         42.59 |      0.8027      |      3.4332      |      0           |      0.01        |      0.0955      |      0.4862      |     40.526       |     8.7835 |    83.4913 |
| share_global_cumulative_luc_co2                              |    4137 |       420 |          9.22 |      0.5944      |      1.9171      |     -0.471       |      0.008       |      0.081       |      0.357       |     16.057       |     5.5374 |    32.4201 |
| share_global_cumulative_oil_co2                              |    4471 |        86 |          1.89 |      0.4396      |      2.0878      |      0           |      0.005       |      0.034       |      0.242       |     30.208       |    11.6055 |   150.555  |
| share_global_cumulative_other_co2                            |     966 |      3591 |         78.8  |      2.1739      |      7.4952      |      0           |      0.1232      |      0.26        |      0.8828      |     39.929       |     4.4191 |    17.9036 |
| share_global_flaring_co2                                     |    4494 |        63 |          1.38 |      0.4673      |      1.605       |      0           |      0           |      0           |      0.1427      |     19.547       |     6.1004 |    44.2184 |
| share_global_gas_co2                                         |    2616 |      1941 |         42.59 |      0.8027      |      2.3635      |      0           |      0.018       |      0.127       |      0.691       |     25.964       |     6.8624 |    54.0945 |
| share_global_luc_co2                                         |    4137 |       420 |          9.22 |      0.566       |      2.4707      |     -5.838       |      0           |      0.032       |      0.325       |     40.957       |     8.9147 |    96.966  |
| share_global_oil_co2                                         |    4471 |        86 |          1.89 |      0.4271      |      1.6998      |      0           |      0.007       |      0.038       |      0.218       |     23.898       |     9.5566 |   108.327  |
| share_global_other_co2                                       |     966 |      3591 |         78.8  |      2.1739      |      7.2748      |      0           |      0.097       |      0.297       |      1.038       |     44.381       |     4.5802 |    19.9538 |
| share_of_temperature_change_from_ghg                         |    4494 |        63 |          1.38 |      0.4673      |      1.6707      |      0           |      0.011       |      0.084       |      0.265       |     20.292       |     8.2014 |    80.2346 |
| temperature_change_from_ch4                                  |    4221 |       336 |          7.37 |      0.0016      |      0.0047      |     -0.001       |      0           |      0           |      0.001       |      0.048       |     6.0399 |    41.3529 |
| temperature_change_from_co2                                  |    4494 |        63 |          1.38 |      0.0045      |      0.0178      |      0           |      0           |      0.001       |      0.002       |      0.238       |     8.9116 |    94.3537 |
| temperature_change_from_ghg                                  |    4494 |        63 |          1.38 |      0.0063      |      0.0228      |      0           |      0           |      0.001       |      0.004       |      0.286       |     8.2198 |    80.4302 |
| temperature_change_from_n2o                                  |    4221 |       336 |          7.37 |      0.0003      |      0.001       |      0           |      0           |      0           |      0           |      0.011       |     6.4966 |    49.9373 |
| total_ghg                                                    |    4179 |       378 |          8.29 |    241.742       |    911.27        |     -0.003       |      8.506       |     46.38        |    127.712       |  12524.1         |     8.625  |    87.779  |
| total_ghg_excluding_lucf                                     |    4146 |       411 |          9.02 |    185.128       |    824.331       |      0.004       |      3.4285      |     17.4995      |     77.9248      |  12091.8         |     9.62   |   105.929  |
| trade_co2                                                    |    2514 |      2043 |         44.83 |     -0.1148      |    124.018       |  -1604.43        |     -0.807       |      2.8345      |     12.2752      |    573.595       |    -7.2893 |    76.4196 |
| trade_co2_share                                              |    2514 |      2043 |         44.83 |     30.2677      |     71.6335      |    -98.281       |     -4.6085      |     14.05        |     42.1128      |   1023.04        |     5.076  |    47.3694 |
| access_to_electricity_of_population                          |    3618 |       939 |         20.61 |     78.8114      |     30.3206      |      1.2523      |     59.3503      |     98.2015      |    100           |    100           |    -1.1973 |    -0.0571 |
| access_to_clean_fuels_for_cooking                            |    3501 |      1056 |         23.17 |     63.4757      |     39.0296      |      0           |     23.5         |     83.4         |    100           |    100           |    -0.5175 |    -1.4102 |
| renewable_electricity_generating_capacity_per_capita         |    2675 |      1882 |         41.3  |    113.926       |    245.63        |      0           |      3.825       |     32.88        |    112.36        |   3060.19        |     5.3424 |    40.0268 |
| financial_flows_to_developing_countries_us                   |    1560 |      2997 |         65.77 |      9.4224e+07  |      2.98154e+08 |      0           | 260000           |      5.665e+06   |      5.53475e+07 |      5.20231e+09 |     8.3883 |   102.367  |
| renewable_energy_share_in_the_total_final_energy_consumption |    3434 |      1123 |         24.64 |     32.8497      |     29.8627      |      0           |      6.72        |     23.765       |     55.3375      |     96.04        |     0.6654 |    -0.9139 |
| electricity_from_fossil_fuels_twh                            |    3606 |       951 |         20.87 |     71.2003      |    349.052       |      0           |      0.29        |      2.995       |     28.135       |   5184.13        |     9.366  |    99.2274 |
| electricity_from_nuclear_twh                                 |    3501 |      1056 |         23.17 |     13.558       |     73.2242      |      0           |      0           |      0           |      0           |    809.41        |     8.5381 |    80.4606 |
| electricity_from_renewables_twh                              |    3606 |       951 |         20.87 |     24.1803      |    104.722       |      0           |      0.05        |      1.56        |     10.035       |   2184.94        |    11.0266 |   165.101  |
| low_carbon_electricity_electricity                           |    3585 |       972 |         21.33 |     37.1007      |     34.2378      |      0           |      4.0435      |     28.2673      |     64.6298      |    100           |     0.4984 |    -1.1523 |
| primary_energy_consumption_per_capita_kwhperson              |    3627 |       930 |         20.41 |  25817.3         |  34957.8         |      0           |   3098.61        |  12996.3         |  33813.7         | 262586           |     2.6257 |     8.445  |
| energy_intensity_level_of_primary_energy_mj2017_ppp_gdp      |    3422 |      1135 |         24.91 |      5.3472      |      3.5141      |      1.03        |      3.2         |      4.325       |      6.0375      |     32.57        |     2.6316 |     9.6862 |
| value_co2_emissions_kt_by_country                            |    3224 |      1333 |         29.25 | 160715           | 773214           |     10           |   2110           |  11020           |  63290           |      1.07072e+07 |     9.3419 |    98.0229 |
| renewables_equivalent_primary_energy                         |    1533 |      3024 |         66.36 |     11.8724      |     14.9255      |      0           |      2.133       |      6.1784      |     16.7077      |     86.8366      |     2.2594 |     6.1159 |
| gdp_growth                                                   |    3318 |      1239 |         27.19 |      3.4624      |      5.6838      |    -62.0759      |      1.4234      |      3.5791      |      5.8422      |    123.14        |     2.5519 |    75.2145 |
| gdp_per_capita                                               |    3352 |      1205 |         26.44 |  13112.9         |  19399.3         |    111.927       |   1330.89        |   4548.72        |  15428.8         | 123514           |     2.3616 |     6.3342 |
| land_area_km2                                                |    3627 |       930 |         20.41 | 637066           |      1.5893e+06  |     21           |  27750           | 118484           | 527968           |      9.98467e+06 |     4.6219 |    22.2469 |
| latitude                                                     |    3627 |       930 |         20.41 |     18.4363      |     24.3651      |    -40.9006      |      3.2028      |     17.0608      |     39.3999      |     64.9631      |    -0.2453 |    -0.6522 |
| longitude                                                    |    3627 |       930 |         20.41 |     14.8537      |     66.0624      |   -175.198       |    -10.9408      |     19.1451      |     45.0792      |    178.065       |    -0.0307 |     0.4967 |
| density_pkm2                                                 |    4011 |       546 |         11.98 |    356.576       |   1997.87        |      2           |     34           |     89           |    214           |  26337           |    11.8668 |   148.34   |
| agricultural_land                                            |    3885 |       672 |         14.75 |     39.1849      |     21.7305      |      0.6         |     21.8         |     39.7         |     55.1         |     82.6         |     0.0856 |    -0.9459 |
| armed_forces_size                                            |    3549 |      1008 |         22.12 | 160550           | 381539           |      0           |  11000           |  31000           | 146000           |      3.031e+06   |     5.0366 |    29.9785 |
| birth_rate                                                   |    3906 |       651 |         14.29 |     20.0123      |      9.8565      |      5.9         |     10.9         |     17.87        |     28.64        |     46.08        |     0.5928 |    -0.806  |
| calling_code                                                 |    4011 |       546 |         11.98 |    358.382       |    324.722       |      1           |     66           |    255           |    507           |   1876           |     1.1859 |     1.4966 |
| co2_emissions                                                |    3885 |       672 |         14.75 | 181389           | 843049           |     11           |   2739           |  12963           |  69259           |      9.89304e+06 |     9.4244 |    98.507  |
| cpi                                                          |    3675 |       882 |         19.35 |    191.316       |    400.191       |     99.03        |    114.11        |    125.08        |    157.58        |   4583.71        |     9.1774 |    89.9052 |
| cpi_change                                                   |    3696 |       861 |         18.89 |      6.7824      |     24.5839      |     -4.3         |      1           |      2.3         |      4.175       |    254.9         |     8.222  |    73.0172 |
| fertility_rate                                               |    3885 |       672 |         14.75 |      2.6692      |      1.2619      |      0.98        |      1.69        |      2.22        |      3.57        |      6.91        |     0.961  |    -0.0195 |
| forested_area                                                |    3885 |       672 |         14.75 |     31.3741      |     23.2958      |      0           |     11           |     31.8         |     46.9         |     98.3         |     0.5192 |    -0.4494 |
| gasoline_price                                               |    3654 |       903 |         19.82 |      1.0014      |      0.3696      |      0           |      0.75        |      0.98        |      1.23        |      2           |     0.0587 |    -0.0292 |
| gross_primary_education_enrollment                           |    3885 |       672 |         14.75 |    102.463       |     13.2085      |     23.4         |     99           |    102.6         |    108.1         |    142.5         |    -0.9817 |     7.6132 |
| gross_tertiary_education_enrollment                          |    3780 |       777 |         17.05 |     38.4467      |     29.2781      |      0.8         |     12.225       |     31.35        |     63.25        |    136.6         |     0.5961 |    -0.5477 |
| infant_mortality                                             |    3906 |       651 |         14.29 |     21.0425      |     19.3455      |      1.4         |      5.9         |     13.8         |     32.7         |     84.5         |     1.1649 |     0.5847 |
| life_expectancy                                              |    3864 |       693 |         15.21 |     72.3772      |      7.461       |     52.8         |     67.05        |     73.5         |     77.6         |     85.4         |    -0.5512 |    -0.3815 |
| maternal_mortality_ratio                                     |    3738 |       819 |         17.97 |    159.214       |    233.592       |      2           |     12           |     52.5         |    186           |   1150           |     2.1727 |     4.7744 |
| minimum_wage                                                 |    3129 |      1428 |         31.34 |      2.2043      |      2.9572      |      0.01        |      0.41        |      1.05        |      2.46        |     13.59        |     2.1696 |     4.0253 |
| out_of_pocket_health_expenditure                             |    3885 |       672 |         14.75 |     32.8719      |     19.0996      |      0.2         |     17.6         |     30.9         |     44.2         |     81.6         |     0.5631 |    -0.3553 |
| physicians_per_thousand                                      |    3885 |       672 |         14.75 |      1.8697      |      1.6803      |      0.01        |      0.37        |      1.56        |      2.98        |      8.42        |     0.9833 |     0.7544 |
| population_labor_force_participation                         |    3654 |       903 |         19.82 |     62.7707      |     10.5277      |     38           |     56           |     62.7         |     69.8         |     86.8         |    -0.0237 |    -0.3546 |
| tax_revenue                                                  |    3486 |      1071 |         23.5  |     16.5976      |      6.9723      |      0           |     11.7         |     16.4         |     21.3         |     37.2         |     0.0782 |     0.0218 |
| total_tax_rate                                               |    3780 |       777 |         17.05 |     40.7633      |     20.5778      |      8           |     30.6         |     37.2         |     47.8         |    219.6         |     3.9417 |    30.2132 |
| unemployment_rate                                            |    3654 |       903 |         19.82 |      6.8544      |      5.0722      |      0.09        |      3.35        |      5.36        |      9.47        |     28.18        |     1.3618 |     1.8469 |
| urban_population                                             |    3927 |       630 |         13.82 |      2.25207e+07 |      7.57859e+07 |   5464           |      1.16283e+06 |      4.71689e+06 |      1.59247e+07 |      8.42934e+08 |     8.189  |    77.9517 |

</details>


---

## Rozklady zmiennych

Analiza rozkladow kluczowych zmiennych pozwala zidentyfikowac asymetrie, wartosci odstajace i potrzebe transformacji.

![Figure 1](figures\eda\hist_co2_per_capita.png)

![Figure 2](figures\eda\box_co2_per_capita.png)

![Figure 3](figures\eda\hist_gdp.png)

![Figure 4](figures\eda\box_gdp.png)

### Wnioski o rozkladach

- Emisje CO2 i PKB maja silnie prawoskosne rozklady (wiekszosc krajow ma niskie wartosci)

- CO2 per capita jest bardziej zrownowazony, ale nadal z prawoskosnoscia

- Rozklady sugeruja potrzebe transformacji logarytmicznej dla modelowania


---

## Analiza korelacji

### Najsilniejsze korelacje

| var1                       | var2                       |   correlation |
|:---------------------------|:---------------------------|--------------:|
| co2                        | primary_energy_consumption |          0.99 |
| gdp                        | primary_energy_consumption |          0.97 |
| co2                        | gdp                        |          0.95 |
| co2                        | coal_co2                   |          0.94 |
| gdp                        | oil_co2                    |          0.93 |
| primary_energy_consumption | oil_co2                    |          0.92 |
| primary_energy_consumption | coal_co2                   |          0.88 |
| oil_co2                    | gas_co2                    |          0.87 |
| co2                        | oil_co2                    |          0.86 |
| gdp                        | coal_co2                   |          0.81 |
| population                 | coal_co2                   |          0.79 |
| gdp                        | gas_co2                    |          0.78 |
| primary_energy_consumption | gas_co2                    |          0.77 |
| co2                        | population                 |          0.76 |
| gdp                        | population                 |          0.71 |

![Macierz korelacji kluczowych zmiennych](figures\eda\correlation_heatmap.png)

*Figure 5: Macierz korelacji kluczowych zmiennych*

### Wnioski z analizy korelacji

- Silna korelacja miedzy PKB a calkowitymi emisjami CO2

- Umiarkowana korelacja miedzy PKB per capita a emisjami per capita

- Zuzycie energii silnie skorelowane z emisjami


---

## Trendy czasowe

### Globalne trendy roczne

|   year |   co2_sum |   co2_mean |   co2_per_capita_mean |     gdp_sum |
|-------:|----------:|-----------:|----------------------:|------------:|
|   2000 |   24723.2 |     115.53 |                  5.04 | 5.98434e+13 |
|   2001 |   24909.4 |     116.4  |                  5.09 | 6.15937e+13 |
|   2002 |   25462.4 |     118.98 |                  5.06 | 6.3701e+13  |
|   2003 |   26817   |     125.31 |                  5.21 | 6.63146e+13 |
|   2004 |   27699.9 |     129.44 |                  5.28 | 7.00257e+13 |
|   2005 |   28653.3 |     133.89 |                  5.29 | 7.36544e+13 |
|   2006 |   29597.1 |     138.3  |                  5.38 | 7.78749e+13 |
|   2007 |   30444.2 |     142.26 |                  5.39 | 8.21827e+13 |
|   2008 |   30984.1 |     144.79 |                  5.35 | 8.47115e+13 |
|   2009 |   30490.8 |     142.48 |                  5.11 | 8.47844e+13 |

### Zmiana 2000-2020

| Metric            | Value          |
|:------------------|:---------------|
| Emisje CO2 w 2000 | 24,723 mln ton |
| Emisje CO2 w 2020 | 34,310 mln ton |
| Zmiana procentowa | +38.8%         |

![Figure 6](figures\eda\trend_co2_global.png)

![Figure 7](figures\eda\trend_co2_by_region.png)


---

## Analiza regionalna

| region        |   countries |   co2_total |   co2_mean |   co2_per_capita_mean |   gdp_total |   population_total |
|:--------------|------------:|------------:|-----------:|----------------------:|------------:|-------------------:|
| Africa        |          54 |    25038.2  |      22.08 |                  1.12 | 8.95651e+13 |        2.27516e+10 |
| Asia          |          49 |   331562    |     322.22 |                  6.96 | 8.29081e+14 |        8.87677e+10 |
| Europe        |          44 |   125432    |     145.68 |                  7.24 | 4.40729e+14 |        1.54612e+10 |
| North America |          23 |   143040    |     296.15 |                  5.03 | 4.04748e+14 |        1.1298e+10  |
| Oceania       |          14 |     9174.93 |      31.21 |                  3.79 | 2.3785e+13  |        7.6779e+08  |
| South America |          12 |    21132.7  |      83.86 |                  2.68 | 1.05823e+14 |        8.1778e+09  |

Azja i Ameryka Polnocna dominuja pod wzgledem calkowitych emisji CO2, ale emisje per capita sa najwyzsze w Ameryce Polnocnej i Oceanii.


---

## Kluczowe zaleznosci (scatter plots)

![Figure 8](figures\eda\scatter_gdp_co2.png)

![Figure 9](figures\eda\scatter_gdp_co2_per_capita.png)

![Figure 10](figures\eda\scatter_population_co2.png)

### Wnioski

- Widoczna dodatnia zaleznosc miedzy PKB a emisjami CO2

- Zaleznosc jest nieliniowa - kraje o bardzo wysokim PKB maja zroznicowane emisje

- Sugeruje to potencjalny efekt krzywej Kuznetsa (EKC)


---

## Podsumowanie

**Kluczowe obserwacje:**

1. Rozklady emisji i PKB sa silnie prawoskosne - wymagaja transformacji log

2. Silna korelacja miedzy PKB a emisjami calkowitymi

3. Emisje globalne rosly w okresie 2000-2020

4. Duze zroznicowanie regionalne w emisjach per capita

5. Widoczne wartosci odstajace (kraje naftowe, Chiny)

**Rekomendacje dla dalszej analizy:**

- Utworzenie zmiennych log-transformowanych

- Dodanie zmiennej kwadratowej PKB dla testu krzywej Kuznetsa

- Szczegolowa analiza outlierow

- Analiza brakow danych i imputacja
