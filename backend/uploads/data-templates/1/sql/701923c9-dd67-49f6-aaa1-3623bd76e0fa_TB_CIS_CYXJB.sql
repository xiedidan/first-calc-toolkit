DROP TABLE IF EXISTS "TB_CIS_CYXJB";
CREATE TABLE "TB_CIS_CYXJB" (
    "YLJGDM" varchar(33),
    "CYXJLSH" varchar(96),
    "JZLSH" varchar(96),
    "KS" varchar(54),
    "KSMC" varchar(108),
    "BRZSY" varchar(96),
    "CH" varchar(24),
    "XM" varchar(108),
    "XB" varchar(2),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "ZYCS" numeric,
    "JZLX" varchar(5),
    "ZYH" varchar(27),
    "ZYBAH" varchar(27),
    "RYSJ" timestamp,
    "CYSJ" timestamp,
    "ZYTS" varchar(8),
    "MZZDBM" varchar(750),
    "MZZDMC" varchar(1500),
    "RYXYZDBM" varchar(750),
    "RYXYZDMC" varchar(1500),
    "RYZYBMDM" varchar(750),
    "RYZYBMMC" varchar(1500),
    "RYZYZHDM" varchar(750),
    "RYZYZHMC" varchar(1500),
    "CYXYZDBM" varchar(750),
    "CYXYZDMC" varchar(1500),
    "CZYZBMDM" varchar(750),
    "CZYZBMMC" varchar(1500),
    "CZYZHDM" varchar(750),
    "CZYZHMC" varchar(1500),
    "RYZZTZ" varchar(3000),
    "RYQK" varchar(3000),
    "JCHZ" varchar(6000),
    "TSJC" varchar(3000),
    "ZLGC" varchar(3000),
    "HBZ" varchar(1536),
    "CYQK" varchar(3000),
    "CYZZTZ" varchar(3000),
    "CYYZ" varchar(3000),
    "YPMC" varchar(2250),
    "QTXX" varchar(2250),
    "ZLJGDM" varchar(2),
    "ZLJGMS" varchar(1536),
    "ZZYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "BQMC" varchar(108),
    "BQDM" varchar(54),
    "BFH" varchar(15),
    "YXFZJCJG" varchar(1500),
    "SJYSXM" varchar(108),
    "SJYSGH" varchar(54),
    "ZYYSQMRQSJ" timestamp,
    "SJYSQMRQSJ" timestamp,
    "ZYSZGCJG" varchar(1500),
    "ZZZF" varchar(150),
    "ZYJZFF" varchar(150),
    "ZYYYFF" varchar(150),
    "SSJCZBM" varchar(192),
    "SSJCZKSRQSJ" timestamp,
    "MZFFDM" varchar(30),
    "SSGC" varchar(3000),
    "SSQKLBDM" varchar(30),
    "SSQKYHDJDM" varchar(30),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_CYXJB" IS '出院小结表';
COMMENT ON COLUMN "TB_CIS_CYXJB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYXJLSH" IS '出院小结流水号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."KS" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CH" IS '床号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."XM" IS '姓名';
COMMENT ON COLUMN "TB_CIS_CYXJB"."XB" IS '性别';
COMMENT ON COLUMN "TB_CIS_CYXJB"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_CYXJB"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_CYXJB"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYCS" IS '住院次数';
COMMENT ON COLUMN "TB_CIS_CYXJB"."JZLX" IS '就诊类型';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYBAH" IS '住院病案号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYSJ" IS '入院时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYSJ" IS '出院时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYTS" IS '住院天数';
COMMENT ON COLUMN "TB_CIS_CYXJB"."MZZDBM" IS '门诊诊断编码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."MZZDMC" IS '门诊诊断名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYXYZDBM" IS '入院西医诊断编码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYXYZDMC" IS '入院西医诊断名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYZYBMDM" IS '入院中医病名代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYZYBMMC" IS '入院中医病名名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYZYZHDM" IS '入院中医证候代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYZYZHMC" IS '入院中医证候名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYXYZDBM" IS '出院西医诊断编码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYXYZDMC" IS '出院西医诊断名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CZYZBMDM" IS '出院中医病名代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CZYZBMMC" IS '出院中医病名名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CZYZHDM" IS '出院中医证候代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CZYZHMC" IS '出院中医证候名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYZZTZ" IS '入院时主要症状及体征';
COMMENT ON COLUMN "TB_CIS_CYXJB"."RYQK" IS '入院情况';
COMMENT ON COLUMN "TB_CIS_CYXJB"."JCHZ" IS '实验室检查及主要会诊';
COMMENT ON COLUMN "TB_CIS_CYXJB"."TSJC" IS '住院期间特殊检查';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZLGC" IS '诊疗过程';
COMMENT ON COLUMN "TB_CIS_CYXJB"."HBZ" IS '合并症';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYQK" IS '出院时情况';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYZZTZ" IS '出院时症状与体征';
COMMENT ON COLUMN "TB_CIS_CYXJB"."CYYZ" IS '出院医嘱';
COMMENT ON COLUMN "TB_CIS_CYXJB"."YPMC" IS '主要药品名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."QTXX" IS '其他重要信息';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZLJGDM" IS '治疗结果代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZLJGMS" IS '治疗结果描述';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_CYXJB"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_CYXJB"."BQDM" IS '病区代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."YXFZJCJG" IS '阳性辅助检查结果';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SJYSXM" IS '上级医师姓名';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SJYSGH" IS '上级医师编号';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYYSQMRQSJ" IS '住院医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SJYSQMRQSJ" IS '上级医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYSZGCJG" IS '中医" 四诊 "观察结果';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYJZFF" IS '中药煎煮方法';
COMMENT ON COLUMN "TB_CIS_CYXJB"."ZYYYFF" IS '中药用药方法';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SSJCZBM" IS '手术及操作编码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SSJCZKSRQSJ" IS '手术及操作开始日期时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."MZFFDM" IS '麻醉方法代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SSGC" IS '手术过程';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SSQKLBDM" IS '手术切口类别代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."SSQKYHDJDM" IS '手术切口愈合等级代码';
COMMENT ON COLUMN "TB_CIS_CYXJB"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_CYXJB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_CYXJB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_CYXJB"."YLYL2" IS '预留二';