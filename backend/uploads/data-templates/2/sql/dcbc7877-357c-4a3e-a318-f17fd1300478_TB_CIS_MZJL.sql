DROP TABLE IF EXISTS "TB_CIS_MZJL";
CREATE TABLE "TB_CIS_MZJL" (
    "YLJGDM" varchar(33),
    "MZJLLSH" varchar(96),
    "MZZYBZ" varchar(2),
    "JZLSH" varchar(96),
    "MZZYH" varchar(27),
    "MZSQFSJLLSH" varchar(96),
    "DZSQDBH" varchar(30),
    "SSMXLSH" varchar(75),
    "KSDM" varchar(54),
    "KSMC" varchar(108),
    "BRZSY" varchar(96),
    "NLS" numeric(3,0),
    "NLY" varchar(12),
    "NLH" varchar(48),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "SSJBH" varchar(15),
    "TZKG" numeric(6,2),
    "SGCM" numeric(5,1),
    "TGJC" varchar(750),
    "ABOXXDM" varchar(2),
    "RHXXDM" varchar(2),
    "SQZDBM" varchar(750),
    "SQZDMC" varchar(1500),
    "SHZDBM" varchar(750),
    "SHZDMC" varchar(1500),
    "SSJCZBM" varchar(75),
    "SSJCZMC" varchar(120),
    "SSKSSJ" timestamp,
    "SSJSSJ" timestamp,
    "SSTWDM" varchar(30),
    "MZFFDM" varchar(30),
    "MZFFMC" varchar(150),
    "QGCGFL" varchar(150),
    "MZYWMC" varchar(384),
    "MZYWDM" varchar(300),
    "MZTW" varchar(150),
    "HXLXDM" varchar(2),
    "MZMS" varchar(3000),
    "MZHBZBZDM" varchar(2),
    "ZLGCMS" varchar(3000),
    "CCGC" varchar(3000),
    "MZYSXHFJBZDM" varchar(2),
    "MZXG" varchar(750),
    "MZQYY" varchar(750),
    "MZKSRQSJ" timestamp,
    "SSJSRQSJ" timestamp,
    "MZQJTSHTFQKJCL" varchar(3000),
    "CSSSRQSJ" timestamp,
    "SZSYXM" varchar(75),
    "SXPZDM" varchar(15),
    "SXL" numeric(4,0),
    "SXLJLDW" varchar(15),
    "SXFYBZ" varchar(2),
    "SXRQSJ" timestamp,
    "CXLML" numeric(5,0),
    "HZQXDM" varchar(2),
    "MZYSXM" varchar(108),
    "MZYSGH" varchar(54),
    "SSYSGH" varchar(54),
    "SSYSXM" varchar(108),
    "MZYSQMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_MZJL" IS '麻醉记录';
COMMENT ON COLUMN "TB_CIS_MZJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZJLLSH" IS '麻醉记录流水号';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_CIS_MZJL"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZZYH" IS '门诊/住院号';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZSQFSJLLSH" IS '麻醉术前访视记录流水号';
COMMENT ON COLUMN "TB_CIS_MZJL"."DZSQDBH" IS '电子申请单编号';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSMXLSH" IS '手术明细流水号';
COMMENT ON COLUMN "TB_CIS_MZJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_MZJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_MZJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_MZJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_MZJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_MZJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSJBH" IS '手术间编号';
COMMENT ON COLUMN "TB_CIS_MZJL"."TZKG" IS '体重(kg)';
COMMENT ON COLUMN "TB_CIS_MZJL"."SGCM" IS '身高(cm)';
COMMENT ON COLUMN "TB_CIS_MZJL"."TGJC" IS '体格检查';
COMMENT ON COLUMN "TB_CIS_MZJL"."ABOXXDM" IS 'ABO 血型代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."RHXXDM" IS 'Rh 血型代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."SQZDBM" IS '术前诊断编码';
COMMENT ON COLUMN "TB_CIS_MZJL"."SQZDMC" IS '术前诊断名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."SHZDBM" IS '术后诊断编码';
COMMENT ON COLUMN "TB_CIS_MZJL"."SHZDMC" IS '术后诊断名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSJCZBM" IS '手术及操作编码';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSJCZMC" IS '手术及操作名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSKSSJ" IS '手术开始时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSJSSJ" IS '手术结束时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSTWDM" IS '手术体位代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZFFDM" IS '麻醉方法代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZFFMC" IS '麻醉方法名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."QGCGFL" IS '气管插管分类';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYWMC" IS '麻醉药物名称';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYWDM" IS '麻醉药物代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZTW" IS '麻醉体位';
COMMENT ON COLUMN "TB_CIS_MZJL"."HXLXDM" IS '呼吸类型代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZMS" IS '麻醉描述';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZHBZBZDM" IS '麻醉合并症标志代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."ZLGCMS" IS '诊疗过程描述';
COMMENT ON COLUMN "TB_CIS_MZJL"."CCGC" IS '穿刺过程';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYSXHFJBZDM" IS '美国麻醉医师协会 (ASA)分级标准代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZXG" IS '麻醉效果';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZQYY" IS '麻醉前用药';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZKSRQSJ" IS '麻醉开始日期时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSJSRQSJ" IS '手术结束日期时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZQJTSHTFQKJCL" IS '麻醉期间特殊或突发情况及处理';
COMMENT ON COLUMN "TB_CIS_MZJL"."CSSSRQSJ" IS '出手术室日期时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."SZSYXM" IS '术中输液项目';
COMMENT ON COLUMN "TB_CIS_MZJL"."SXPZDM" IS '输血品种代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."SXL" IS '输血量';
COMMENT ON COLUMN "TB_CIS_MZJL"."SXLJLDW" IS '输血量计量单位';
COMMENT ON COLUMN "TB_CIS_MZJL"."SXFYBZ" IS '输血反应标志';
COMMENT ON COLUMN "TB_CIS_MZJL"."SXRQSJ" IS '输血日期时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."CXLML" IS '出血量（mL)';
COMMENT ON COLUMN "TB_CIS_MZJL"."HZQXDM" IS '患者去向代码';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYSXM" IS '麻醉医师姓名';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYSGH" IS '麻醉医师编号';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSYSGH" IS '手术医生工号';
COMMENT ON COLUMN "TB_CIS_MZJL"."SSYSXM" IS '手术医生姓名';
COMMENT ON COLUMN "TB_CIS_MZJL"."MZYSQMRQSJ" IS '麻醉医师签名日期时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_MZJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_MZJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_MZJL"."YLYL2" IS '预留二';