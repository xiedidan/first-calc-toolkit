DROP TABLE IF EXISTS "TB_YL_HZJL";
CREATE TABLE "TB_YL_HZJL" (
    "YLJGDM" varchar(33),
    "SQHZID" varchar(48),
    "MZZYBZ" varchar(2),
    "JZLSH" varchar(48),
    "BRZSY" varchar(96),
    "HZZJHM" varchar(48),
    "HZZJLX" varchar(3),
    "SQSJ" timestamp,
    "HZKSSJ" timestamp,
    "HZJSSJ" timestamp,
    "SQKSBM" varchar(30),
    "SQKSMC" varchar(45),
    "SQYSGH" varchar(24),
    "SQYSXM" varchar(108),
    "SQLY" varchar(768),
    "HZYJ" varchar(1536),
    "FJHZYJ" varchar(1536),
    "CYHZZJ" varchar(3072),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_YL_HZJL" IS '会诊记录表';
COMMENT ON COLUMN "TB_YL_HZJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_YL_HZJL"."SQHZID" IS '申请会诊 ID';
COMMENT ON COLUMN "TB_YL_HZJL"."MZZYBZ" IS '门诊住院标志';
COMMENT ON COLUMN "TB_YL_HZJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_YL_HZJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_YL_HZJL"."HZZJHM" IS '患者证件号码';
COMMENT ON COLUMN "TB_YL_HZJL"."HZZJLX" IS '患者证件类型';
COMMENT ON COLUMN "TB_YL_HZJL"."SQSJ" IS '申请时间';
COMMENT ON COLUMN "TB_YL_HZJL"."HZKSSJ" IS '会诊开始时间';
COMMENT ON COLUMN "TB_YL_HZJL"."HZJSSJ" IS '会诊结束时间';
COMMENT ON COLUMN "TB_YL_HZJL"."SQKSBM" IS '申请科室编码';
COMMENT ON COLUMN "TB_YL_HZJL"."SQKSMC" IS '申请科室名称';
COMMENT ON COLUMN "TB_YL_HZJL"."SQYSGH" IS '申请医生工号';
COMMENT ON COLUMN "TB_YL_HZJL"."SQYSXM" IS '申请医生姓名';
COMMENT ON COLUMN "TB_YL_HZJL"."SQLY" IS '申请理由';
COMMENT ON COLUMN "TB_YL_HZJL"."HZYJ" IS '会诊意见';
COMMENT ON COLUMN "TB_YL_HZJL"."FJHZYJ" IS '附加会诊意见';
COMMENT ON COLUMN "TB_YL_HZJL"."CYHZZJ" IS '参与会诊专家';
COMMENT ON COLUMN "TB_YL_HZJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_YL_HZJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_YL_HZJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_YL_HZJL"."YLYL2" IS '预留二';