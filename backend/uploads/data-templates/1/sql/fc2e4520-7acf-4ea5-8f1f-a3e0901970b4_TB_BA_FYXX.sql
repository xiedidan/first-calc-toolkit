DROP TABLE IF EXISTS "TB_BA_FYXX";
CREATE TABLE "TB_BA_FYXX" (
    "YLJGDM" varchar(33),
    "FYID" varchar(96),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "ZFY" numeric(12,3),
    "ZFJE" numeric(12,3),
    "QTZF" numeric(12,3),
    "YLFWF" numeric(12,3),
    "ZYBZLZF" numeric(12,3),
    "ZYBZLZHZF" numeric(12,3),
    "ZLCZF" numeric(12,3),
    "HLF" numeric(12,3),
    "QTFY" numeric(12,3),
    "BLZDF" numeric(12,3),
    "SYSZDF" numeric(12,3),
    "YXXZDF" numeric(12,3),
    "LCZDXMF" numeric(12,3),
    "FSSZLXMF" numeric(12,3),
    "LCWLZLF" numeric(12,3),
    "SSZLF" numeric(12,3),
    "MZF" numeric(12,3),
    "SSF" numeric(12,3),
    "KFF" numeric(12,3),
    "ZYZDF" numeric(12,3),
    "ZYZLF" numeric(12,3),
    "ZYWZF" numeric(12,3),
    "ZYGSF" numeric(12,3),
    "ZCYJFF" numeric(12,3),
    "ZYTNZLF" numeric(12,3),
    "ZYGCZLF" numeric(12,3),
    "ZYTSZLF" numeric(12,3),
    "ZYQTF" numeric(12,3),
    "ZYTSTPF" numeric(12,3),
    "BZSS" numeric(12,3),
    "XYF" numeric(12,3),
    "KJYWFY" numeric(12,3),
    "ZCYF" numeric(12,3),
    "YLJGZYZJF" numeric(12,3),
    "ZCYF1" numeric(12,3),
    "XF" numeric(12,3),
    "BDBZPF" numeric(12,3),
    "QDBZPF" numeric(12,3),
    "NXYZZPF" numeric(12,3),
    "XBYZZPF" numeric(12,3),
    "JCYYCLF" numeric(12,3),
    "ZLYYCLF" numeric(12,3),
    "SSYYCLF" numeric(12,3),
    "QTF_1" numeric(12,3),
    "BZ" varchar(384),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_BA_FYXX" IS '住院病案费用信息';
COMMENT ON COLUMN "TB_BA_FYXX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_BA_FYXX"."FYID" IS '费用 ID';
COMMENT ON COLUMN "TB_BA_FYXX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_BA_FYXX"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_BA_FYXX"."ZFY" IS '总费用';
COMMENT ON COLUMN "TB_BA_FYXX"."ZFJE" IS '自付金额';
COMMENT ON COLUMN "TB_BA_FYXX"."QTZF" IS '其他支付';
COMMENT ON COLUMN "TB_BA_FYXX"."YLFWF" IS '一般医疗服务费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYBZLZF" IS '中医辨证论治费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYBZLZHZF" IS '中医辨证论治会诊费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZLCZF" IS '一般治疗操作费';
COMMENT ON COLUMN "TB_BA_FYXX"."HLF" IS '护理费';
COMMENT ON COLUMN "TB_BA_FYXX"."QTFY" IS '其他费用';
COMMENT ON COLUMN "TB_BA_FYXX"."BLZDF" IS '病理诊断费';
COMMENT ON COLUMN "TB_BA_FYXX"."SYSZDF" IS '实验室诊断费';
COMMENT ON COLUMN "TB_BA_FYXX"."YXXZDF" IS '影像学诊断费';
COMMENT ON COLUMN "TB_BA_FYXX"."LCZDXMF" IS '临床诊断项目费';
COMMENT ON COLUMN "TB_BA_FYXX"."FSSZLXMF" IS '非手术治疗项目费';
COMMENT ON COLUMN "TB_BA_FYXX"."LCWLZLF" IS '临床物理治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."SSZLF" IS '手术治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."MZF" IS '麻醉费';
COMMENT ON COLUMN "TB_BA_FYXX"."SSF" IS '手术费';
COMMENT ON COLUMN "TB_BA_FYXX"."KFF" IS '康复费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYZDF" IS '中医诊断费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYZLF" IS '中医治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYWZF" IS '中医外治费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYGSF" IS '中医骨伤费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZCYJFF" IS '针刺与灸法费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYTNZLF" IS '中医推拿治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYGCZLF" IS '中医肛肠治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYTSZLF" IS '中医特殊治疗费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYQTF" IS '中医其他';
COMMENT ON COLUMN "TB_BA_FYXX"."ZYTSTPF" IS '中药特殊调配加工费';
COMMENT ON COLUMN "TB_BA_FYXX"."BZSS" IS '辩证施膳';
COMMENT ON COLUMN "TB_BA_FYXX"."XYF" IS '西药费';
COMMENT ON COLUMN "TB_BA_FYXX"."KJYWFY" IS '抗菌药物费用';
COMMENT ON COLUMN "TB_BA_FYXX"."ZCYF" IS '中成药费';
COMMENT ON COLUMN "TB_BA_FYXX"."YLJGZYZJF" IS '医疗机构中药制剂费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZCYF1" IS '中草药费';
COMMENT ON COLUMN "TB_BA_FYXX"."XF" IS '血费';
COMMENT ON COLUMN "TB_BA_FYXX"."BDBZPF" IS '白蛋白类制品费';
COMMENT ON COLUMN "TB_BA_FYXX"."QDBZPF" IS '球蛋白类制品费';
COMMENT ON COLUMN "TB_BA_FYXX"."NXYZZPF" IS '凝血因子类制品费';
COMMENT ON COLUMN "TB_BA_FYXX"."XBYZZPF" IS '细胞因子类制品费';
COMMENT ON COLUMN "TB_BA_FYXX"."JCYYCLF" IS '检查用一次性医用材料费';
COMMENT ON COLUMN "TB_BA_FYXX"."ZLYYCLF" IS '治疗用一次性医用材料费';
COMMENT ON COLUMN "TB_BA_FYXX"."SSYYCLF" IS '手术用一次性医用材料费';
COMMENT ON COLUMN "TB_BA_FYXX"."QTF_1" IS '其他费';
COMMENT ON COLUMN "TB_BA_FYXX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_BA_FYXX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_BA_FYXX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_BA_FYXX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_BA_FYXX"."YLYL2" IS '预留二';