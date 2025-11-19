DROP TABLE IF EXISTS "TB_ZY_YZZB";
CREATE TABLE "TB_ZY_YZZB" (
    "YLJGDM" varchar(33),
    "YZZID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "CFDL" varchar(6),
    "CXBZ" varchar(2),
    "YZXQ" varchar(3),
    "YZMC" varchar(150),
    "HZXM" varchar(108),
    "HZXB" varchar(30),
    "HZNL" varchar(45),
    "HZKS" varchar(48),
    "HZBQ" varchar(48),
    "HZBSH" varchar(48),
    "XDKSBM" varchar(96),
    "XDKSMC" varchar(114),
    "YZXDYSGH" varchar(54),
    "YZXDYSXMXDRXM" varchar(108),
    "YZXDYSSFZHM" varchar(27),
    "YZXDSJ" timestamp,
    "JKWTPG" varchar(1500),
    "BZ" varchar(1536),
    "ZYFA" varchar(1500),
    "KFCSZD" varchar(1500),
    "CFDPSJ" timestamp,
    "CFDPJG" varchar(750),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_YZZB" IS '住院医嘱主表';
COMMENT ON COLUMN "TB_ZY_YZZB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZZID" IS '医嘱主 ID';
COMMENT ON COLUMN "TB_ZY_YZZB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_YZZB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_YZZB"."CFDL" IS '处方大类';
COMMENT ON COLUMN "TB_ZY_YZZB"."CXBZ" IS '撤销标志';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZXQ" IS '医嘱效期';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZMC" IS '医嘱名称';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZXM" IS '患者姓名';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZXB" IS '患者性别';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZNL" IS '患者年龄';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZKS" IS '患者科室';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZBQ" IS '患者病区';
COMMENT ON COLUMN "TB_ZY_YZZB"."HZBSH" IS '患者标识号';
COMMENT ON COLUMN "TB_ZY_YZZB"."XDKSBM" IS '下达科室编码';
COMMENT ON COLUMN "TB_ZY_YZZB"."XDKSMC" IS '下达科室名称';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZXDYSGH" IS '医嘱下达医师编号';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZXDYSXMXDRXM" IS '医嘱下达医师姓名';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZXDYSSFZHM" IS '医嘱下达医师身份证号码';
COMMENT ON COLUMN "TB_ZY_YZZB"."YZXDSJ" IS '医嘱下达时间';
COMMENT ON COLUMN "TB_ZY_YZZB"."JKWTPG" IS '健康问题评估';
COMMENT ON COLUMN "TB_ZY_YZZB"."BZ" IS '说明';
COMMENT ON COLUMN "TB_ZY_YZZB"."ZYFA" IS '治疗方案';
COMMENT ON COLUMN "TB_ZY_YZZB"."KFCSZD" IS '康复措施指导';
COMMENT ON COLUMN "TB_ZY_YZZB"."CFDPSJ" IS '处方点评时间';
COMMENT ON COLUMN "TB_ZY_YZZB"."CFDPJG" IS '处方点评结果';
COMMENT ON COLUMN "TB_ZY_YZZB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_YZZB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_YZZB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_YZZB"."YLYL2" IS '预留二';