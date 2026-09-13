# Condition-Specific Breakdown Across All 8 Degradation Regimes

| Condition                | Method                   |   Precision |   Recall |     F1 | Loc_Error_m   |   Confidence |   Latency_ms |   FPS |
|:-------------------------|:-------------------------|------------:|---------:|-------:|:--------------|-------------:|-------------:|------:|
| Clean_Nominal            | Camera-Only              |      0.1549 |   0.219  | 0.1815 | N/A (2D)      |       0.5707 |       210.59 |   4.7 |
| Clean_Nominal            | LiDAR-Only               |      0.1464 |   0.0833 | 0.1062 | 1.9829        |       0.314  |       210.81 |   4.7 |
| Clean_Nominal            | Late Fusion (Fixed)      |      0.4783 |   0.1571 | 0.2366 | 1.1955        |       0.2143 |       210.81 |   4.7 |
| Clean_Nominal            | Dempster-Shafer          |      0.1111 |   0.1071 | 0.1091 | 1.1111        |       0.4527 |       211.27 |   4.7 |
| Clean_Nominal            | Distance-Adaptive        |      0.461  |   0.1548 | 0.2317 | 0.8647        |       0.2125 |       210.91 |   4.7 |
| Clean_Nominal            | Temporal Fusion          |      0.2731 |   0.1762 | 0.2142 | 1.1725        |       0.4075 |       211.7  |   4.7 |
| Clean_Nominal            | Proposed Adaptive Fusion |      0.1841 |   0.1214 | 0.1463 | 1.4727        |       0.3246 |       214.73 |   4.7 |
| Camera_Degraded          | Camera-Only              |      0.0455 |   0.0024 | 0.0045 | N/A (2D)      |       0.3208 |       176.6  |   5.7 |
| Camera_Degraded          | LiDAR-Only               |      0.1568 |   0.0881 | 0.1128 | 1.9812        |       0.3113 |       176.82 |   5.7 |
| Camera_Degraded          | Late Fusion (Fixed)      |      0.3617 |   0.081  | 0.1323 | 1.6859        |       0.1598 |       176.78 |   5.7 |
| Camera_Degraded          | Dempster-Shafer          |      0.0916 |   0.0833 | 0.0873 | 2.0091        |       0.4002 |       177.16 |   5.6 |
| Camera_Degraded          | Distance-Adaptive        |      0.1875 |   0.0357 | 0.06   | 1.0084        |       0.1342 |       176.88 |   5.7 |
| Camera_Degraded          | Temporal Fusion          |      0.2288 |   0.1286 | 0.1646 | 1.5749        |       0.3203 |       177.59 |   5.6 |
| Camera_Degraded          | Proposed Adaptive Fusion |      0.1208 |   0.069  | 0.0879 | 1.9595        |       0.2907 |       180.26 |   5.5 |
| LiDAR_Degraded           | Camera-Only              |      0.1549 |   0.219  | 0.1815 | N/A (2D)      |       0.5707 |       192.39 |   5.2 |
| LiDAR_Degraded           | LiDAR-Only               |      0.0682 |   0.0071 | 0.0129 | 2.0357        |       0.4782 |       192.42 |   5.2 |
| LiDAR_Degraded           | Late Fusion (Fixed)      |      0.2727 |   0.0143 | 0.0271 | 1.3059        |       0.2926 |       192.41 |   5.2 |
| LiDAR_Degraded           | Dempster-Shafer          |      1      |   0.0143 | 0.0282 | 0.7173        |       0.1487 |       192.45 |   5.2 |
| LiDAR_Degraded           | Distance-Adaptive        |      1      |   0.0143 | 0.0282 | 0.6667        |       0.1551 |       192.42 |   5.2 |
| LiDAR_Degraded           | Temporal Fusion          |      0.3    |   0.0214 | 0.04   | 1.2630        |       0.4996 |       192.59 |   5.2 |
| LiDAR_Degraded           | Proposed Adaptive Fusion |      1      |   0.0119 | 0.0235 | 0.5311        |       0.5101 |       192.67 |   5.2 |
| Camera_Outage            | Camera-Only              |      0      |   0      | 0      | N/A (2D)      |       0      |       194.06 |   5.2 |
| Camera_Outage            | LiDAR-Only               |      0.1588 |   0.0881 | 0.1133 | 1.9804        |       0.3122 |       194.27 |   5.1 |
| Camera_Outage            | Late Fusion (Fixed)      |      0.3368 |   0.0762 | 0.1243 | 1.9191        |       0.1561 |       194.23 |   5.1 |
| Camera_Outage            | Dempster-Shafer          |      0.0892 |   0.081  | 0.0849 | 2.0386        |       0.3983 |       194.61 |   5.1 |
| Camera_Outage            | Distance-Adaptive        |      0.0435 |   0.0071 | 0.0123 | 2.1614        |       0.1285 |       194.33 |   5.1 |
| Camera_Outage            | Temporal Fusion          |      0.2017 |   0.1119 | 0.144  | 1.8961        |       0.3156 |       194.94 |   5.1 |
| Camera_Outage            | Proposed Adaptive Fusion |      0.1203 |   0.069  | 0.0877 | 1.9585        |       0.2926 |       197.37 |   5.1 |
| Both_Degraded            | Camera-Only              |      0.3684 |   0.0833 | 0.1359 | N/A (2D)      |       0.5303 |       172.79 |   5.8 |
| Both_Degraded            | LiDAR-Only               |      0.0202 |   0.0119 | 0.015  | 2.1589        |       0.5839 |       172.95 |   5.8 |
| Both_Degraded            | Late Fusion (Fixed)      |      0.0422 |   0.0167 | 0.0239 | 1.3267        |       0.3135 |       172.91 |   5.8 |
| Both_Degraded            | Dempster-Shafer          |      1      |   0.031  | 0.06   | 1.5766        |       0.1272 |       173.09 |   5.8 |
| Both_Degraded            | Distance-Adaptive        |      0.9545 |   0.05   | 0.095  | 0.6513        |       0.1181 |       172.96 |   5.8 |
| Both_Degraded            | Temporal Fusion          |      0.0409 |   0.0381 | 0.0395 | 1.2814        |       0.3872 |       173.96 |   5.7 |
| Both_Degraded            | Proposed Adaptive Fusion |      1      |   0.0024 | 0.0048 | 1.8940        |       0.1778 |       174.54 |   5.7 |
| Severe_Camera_Degraded   | Camera-Only              |      0      |   0      | 0      | N/A (2D)      |       0      |       229.81 |   4.4 |
| Severe_Camera_Degraded   | LiDAR-Only               |      0.1561 |   0.0881 | 0.1126 | 1.9798        |       0.3152 |       230.06 |   4.3 |
| Severe_Camera_Degraded   | Late Fusion (Fixed)      |      0.337  |   0.0738 | 0.1211 | 1.9156        |       0.1576 |       230.06 |   4.3 |
| Severe_Camera_Degraded   | Dempster-Shafer          |      0.0912 |   0.081  | 0.0858 | 2.0383        |       0.4007 |       230.49 |   4.3 |
| Severe_Camera_Degraded   | Distance-Adaptive        |      0.0563 |   0.0095 | 0.0163 | 2.0837        |       0.1297 |       230.15 |   4.3 |
| Severe_Camera_Degraded   | Temporal Fusion          |      0.207  |   0.1119 | 0.1453 | 1.8945        |       0.3154 |       230.87 |   4.3 |
| Severe_Camera_Degraded   | Proposed Adaptive Fusion |      0.125  |   0.0714 | 0.0909 | 1.9540        |       0.2948 |       233.67 |   4.3 |
| Severe_LiDAR_Degraded    | Camera-Only              |      0.1549 |   0.219  | 0.1815 | N/A (2D)      |       0.5707 |       273.57 |   3.7 |
| Severe_LiDAR_Degraded    | LiDAR-Only               |      0      |   0      | 0      | 0.0000        |       0      |       273.57 |   3.7 |
| Severe_LiDAR_Degraded    | Late Fusion (Fixed)      |      0      |   0      | 0      | 0.0000        |       0      |       273.57 |   3.7 |
| Severe_LiDAR_Degraded    | Dempster-Shafer          |      0      |   0      | 0      | 0.0000        |       0      |       273.57 |   3.7 |
| Severe_LiDAR_Degraded    | Distance-Adaptive        |      0      |   0      | 0      | 0.0000        |       0      |       273.57 |   3.7 |
| Severe_LiDAR_Degraded    | Temporal Fusion          |      0      |   0      | 0      | 0.0000        |       0      |       273.58 |   3.7 |
| Severe_LiDAR_Degraded    | Proposed Adaptive Fusion |      0      |   0      | 0      | 0.0000        |       0      |       273.57 |   3.7 |
| Combined_Severe_Degraded | Camera-Only              |      0      |   0      | 0      | N/A (2D)      |       0      |       406.94 |   2.5 |
| Combined_Severe_Degraded | LiDAR-Only               |      0      |   0      | 0      | 0.0000        |       0.235  |       406.94 |   2.5 |
| Combined_Severe_Degraded | Late Fusion (Fixed)      |      0      |   0      | 0      | 0.0000        |       0.1175 |       406.94 |   2.5 |
| Combined_Severe_Degraded | Dempster-Shafer          |      0      |   0      | 0      | 0.0000        |       0.0398 |       406.94 |   2.5 |
| Combined_Severe_Degraded | Distance-Adaptive        |      0      |   0      | 0      | 0.0000        |       0.0293 |       406.94 |   2.5 |
| Combined_Severe_Degraded | Temporal Fusion          |      0      |   0      | 0      | 0.0000        |       0      |       406.94 |   2.5 |
| Combined_Severe_Degraded | Proposed Adaptive Fusion |      0      |   0      | 0      | 0.0000        |       0      |       406.96 |   2.5 |
