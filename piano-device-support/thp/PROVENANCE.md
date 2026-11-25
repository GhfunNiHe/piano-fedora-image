# THP 校准来源

`piano-csot-thp-calibration.json` 与 `piano-boe-thp-calibration.json` 由上游
`xiaomipad-8pro-mainline/tools/extract-thp-calibration.py` 生成，输入是**公开 OTA**
里的原厂 THP 配置，不是任何单台机器的分区转储：

| 项 | 值 |
| --- | --- |
| OTA | `piano_images_OS4.0.5.0.XPYCNXM_20261021.0000.00_17.0_cn_*.tgz` |
| 镜像 | `images/super.img` → 逻辑分区 `odm_a` → `/firmware/piano_nova_{csot,boe}_thp_config.ini` |
| CSOT ini sha256 | `32f59bf4d6410b72fc8671efaa2e60dd243c41e281c2f860db8f1ce019518274` |
| BOE ini sha256 | `7312773b68671c7907bee4aba83cdb88e74568aa0fea9ddedaad8f2b1c52d910` |

两份文件同时含手指电极表、`pen`（P81c）与 `m80p`（普通笔）三段笔参数。
重新生成的命令与校验方式见 `docs/upstream-sync.md` 的“THP 触控与笔校准”。
