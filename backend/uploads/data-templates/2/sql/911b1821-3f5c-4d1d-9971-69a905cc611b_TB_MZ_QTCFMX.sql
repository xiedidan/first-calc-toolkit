DROP TABLE IF EXISTS "TB_MZ_QTCFMX";
CREATE TABLE "TB_MZ_QTCFMX" (
    "YLJGDM" varchar(33),
    "CFMXID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "CFZID" varchar(54),
    "YZXH" numeric,
    "YZZH" varchar(75),
    "ZLXMLBBM" varchar(6),
    "XMBZBM" varchar(3),
    "XMBM" varchar(54),
    "XMMC" varchar(96),
    "YNSFXMBM" varchar(75),
    "YNSFXMMC" varchar(300),
    "XMFLBM" varchar(48),
    "XMFLMC" varchar(75),
    "ZXPL" varchar(6),
    "CJFX" varchar(150),
    "CJBB" varchar(150),
    "JCBW" varchar(150),
    "MZFS" varchar(150),
    "YZKSSJ" timestamp,
    "YZTZSJ" timestamp,
    "ZXKSBM" varchar(96),
    "ZXKSMC" varchar(114),
    "ZXRGH" varchar(54),
    "ZXRXM" varchar(108),
    "YZZXSJ" timestamp,
    "BZ" varchar(192),
    "JKWTPG" varchar(3000),
    "KFCSZD" varchar(3000),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_QTCFMX" IS '门诊其他处方明细表';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."CFMXID" IS '处方明细 ID';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."CFZID" IS '处方主 ID';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YZXH" IS '医嘱序号';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YZZH" IS '医嘱组号';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZLXMLBBM" IS '诊疗项目类别编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XMBZBM" IS '项目标准编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XMBM" IS '项目编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XMMC" IS '项目名称';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YNSFXMBM" IS '院内收费项目编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YNSFXMMC" IS '院内收费项目名称';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XMFLBM" IS '项目分类编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XMFLMC" IS '项目分类名称';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZXPL" IS '执行频率';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."CJFX" IS '采集方式';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."CJBB" IS '采标标本';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."JCBW" IS '检查部位';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."MZFS" IS '麻醉方式';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YZKSSJ" IS '医嘱开始时间';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YZTZSJ" IS '医嘱停止时间';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZXRGH" IS '医嘱执行人编号';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."ZXRXM" IS '医嘱执行人姓名';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YZZXSJ" IS '医嘱执行时间';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."BZ" IS '说明';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."JKWTPG" IS '健康问题评估';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."KFCSZD" IS '康复措施指导';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_QTCFMX"."YLYL2" IS '预留二';