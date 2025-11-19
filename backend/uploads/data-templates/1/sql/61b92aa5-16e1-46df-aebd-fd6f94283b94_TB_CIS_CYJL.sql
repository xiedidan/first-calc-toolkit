DROP TABLE IF EXISTS "TB_CIS_CYJL";
CREATE TABLE "TB_CIS_CYJL" (
    "YLJGDM" varchar(33),
    "CYJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "HZXM" varchar(108),
    "XBDM" varchar(2),
    "RYRQSJ" timestamp,
    "CYRQSJ" timestamp,
    "RYZD_XYZDBM" varchar(750),
    "RYZD_XYZDMC" varchar(1500),
    "RYZD_ZYBMDM" varchar(750),
    "RYZD_ZYBMMC" varchar(1500),
    "RYZD_ZYZHDM" varchar(750),
    "RYZD_ZYZHMC" varchar(1500),
    "RYQK" varchar(3000),
    "YXFZJCJG" varchar(1500),
    "ZYSZGCJG" varchar(1500),
    "ZZZF" varchar(150),
    "BZLZXXMS" varchar(1500),
    "ZYJZFF" varchar(150),
    "ZYYYFF" varchar(150),
    "ZLGCMS" varchar(3000),
    "SSGCMS" varchar(3000),
    "CYQK" varchar(3000),
    "CYZD_XYZDBM" varchar(750),
    "CYZD_XYZDMC" varchar(1500),
    "CYZD_ZYBMDM" varchar(750),
    "CYZD_ZYBMMC" varchar(1500),
    "CYZD_ZYZHDM" varchar(750),
    "CYZD_ZYZHMC" varchar(1500),
    "CYSZZYTZ" varchar(1500),
    "CYYZ" varchar(1920),
    "ZYYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZZYSGH" varchar(54),
    "ZRYSXM" varchar(108),
    "ZRYSGH" varchar(54),
    "ZYYSQMRQSJ" timestamp,
    "ZZYSQMRQSJ" timestamp,
    "ZRYSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_CYJL" IS '出院记录';
COMMENT ON COLUMN "TB_CIS_CYJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYJLLSH" IS '出院记录流水号';
COMMENT ON COLUMN "TB_CIS_CYJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_CYJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_CYJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_CYJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_CYJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_CYJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_CYJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_CYJL"."HZXM" IS '患者姓名';
COMMENT ON COLUMN "TB_CIS_CYJL"."XBDM" IS '性别代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYRQSJ" IS '出院日期时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_XYZDBM" IS '入院诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_XYZDMC" IS '入院诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_ZYBMDM" IS '入院诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_ZYBMMC" IS '入院诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_ZYZHDM" IS '入院诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYZD_ZYZHMC" IS '入院诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_CYJL"."YXFZJCJG" IS '阳性辅助检查结果';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYSZGCJG" IS '中医“四诊”观察结果';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_CYJL"."BZLZXXMS" IS '辨证论治详细描述';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYJZFF" IS '中药煎煮方法';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYYYFF" IS '中药用药方法';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_CYJL"."SSGCMS" IS '手术过程描述';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYQK" IS '出院情况';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_XYZDBM" IS '出院诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_XYZDMC" IS '出院诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_ZYBMDM" IS '出院诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_ZYBMMC" IS '出院诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_ZYZHDM" IS '出院诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYZD_ZYZHMC" IS '出院诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYSZZYTZ" IS '出院时症状与体征';
COMMENT ON COLUMN "TB_CIS_CYJL"."CYYZ" IS '出院医嘱';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZRYSXM" IS '主任医师姓名';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZRYSGH" IS '主任医师编号';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZYYSQMRQSJ" IS '住院医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZZYSQMRQSJ" IS '主治医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."ZRYSQMRQSJ" IS '主任医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_CYJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_CYJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_CYJL"."YLYL2" IS '预留二';