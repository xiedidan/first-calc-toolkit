DROP TABLE IF EXISTS "TB_MZ_SFMXB";
CREATE TABLE "TB_MZ_SFMXB" (
    "YLJGDM" varchar(33),
    "SFMXID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "BTFMXID" varchar(54),
    "TFBZ" varchar(2),
    "SFCJBM" varchar(2),
    "YZMXID" varchar(54),
    "SFXMLBBM" varchar(6),
    "FYSRGLBM" varchar(6),
    "FYFSSJ" timestamp,
    "SYJSID" varchar(54),
    "SFJSSJ" timestamp,
    "KDKSBM" varchar(54),
    "KDKSMC" varchar(108),
    "KDYSBH" varchar(54),
    "KDYSXM" varchar(108),
    "KDYSSFZHM" varchar(27),
    "ZXKSBM" varchar(54),
    "ZXKSMC" varchar(108),
    "ZXRYBH" varchar(54),
    "ZXRYXM" varchar(108),
    "ZXRYSFZHM" varchar(27),
    "SFXMBZBM" varchar(3),
    "MXXMBM" varchar(54),
    "MXXMMC" varchar(96),
    "YNSFXMBM" varchar(75),
    "YNSFXMMC" varchar(300),
    "MXXMDW" varchar(18),
    "XMFLBM" varchar(48),
    "XMFLMC" varchar(96),
    "MXXMDJ" numeric(10,4),
    "MXXMSL" numeric(8,3),
    "MXXMYSJE" numeric(10,4),
    "MXXMSSJE" numeric(10,4),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_SFMXB" IS '门诊费用明细表';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SFMXID" IS '收费明细 ID';
COMMENT ON COLUMN "TB_MZ_SFMXB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_SFMXB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_SFMXB"."BTFMXID" IS '被退费明细 ID';
COMMENT ON COLUMN "TB_MZ_SFMXB"."TFBZ" IS '退费标志';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SFCJBM" IS '收费场景编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YZMXID" IS '医嘱明细 ID';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SFXMLBBM" IS '收费项目类别编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."FYSRGLBM" IS '费用收入归类编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."FYFSSJ" IS '费用发生时间';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SYJSID" IS '费用结算 ID';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SFJSSJ" IS '费用结算时间';
COMMENT ON COLUMN "TB_MZ_SFMXB"."KDKSBM" IS '开单科室编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."KDKSMC" IS '开单科室名称';
COMMENT ON COLUMN "TB_MZ_SFMXB"."KDYSBH" IS '开单医生编号';
COMMENT ON COLUMN "TB_MZ_SFMXB"."KDYSXM" IS '开单医生姓名';
COMMENT ON COLUMN "TB_MZ_SFMXB"."KDYSSFZHM" IS '开单医生身份证号码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."ZXKSBM" IS '执行科室编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."ZXKSMC" IS '执行科室名称';
COMMENT ON COLUMN "TB_MZ_SFMXB"."ZXRYBH" IS '执行人员编号';
COMMENT ON COLUMN "TB_MZ_SFMXB"."ZXRYXM" IS '执行人员姓名';
COMMENT ON COLUMN "TB_MZ_SFMXB"."ZXRYSFZHM" IS '执行人员身份证号码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."SFXMBZBM" IS '收费项目标准编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMBM" IS '明细项目编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMMC" IS '明细项目名称';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YNSFXMBM" IS '院内收费项目编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YNSFXMMC" IS '院内收费项目名称';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMDW" IS '明细项目单位';
COMMENT ON COLUMN "TB_MZ_SFMXB"."XMFLBM" IS '项目分类编码';
COMMENT ON COLUMN "TB_MZ_SFMXB"."XMFLMC" IS '项目分类名称';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMDJ" IS '明细项目单价';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMSL" IS '明细项目数量';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMYSJE" IS '明细项目应收金额';
COMMENT ON COLUMN "TB_MZ_SFMXB"."MXXMSSJE" IS '明细项目实收金额';
COMMENT ON COLUMN "TB_MZ_SFMXB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_SFMXB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_SFMXB"."YLYL2" IS '预留二';