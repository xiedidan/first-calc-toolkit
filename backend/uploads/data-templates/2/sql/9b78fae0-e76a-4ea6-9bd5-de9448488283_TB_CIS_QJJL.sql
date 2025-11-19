DROP TABLE IF EXISTS "TB_CIS_QJJL";
CREATE TABLE "TB_CIS_QJJL" (
    "YLJGDM" varchar(33),
    "QJJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "KSDM" varchar(54),
    "KSMC" varchar(108),
    "BQMC" varchar(108),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "JBZDBM" varchar(750),
    "JBZDMC" varchar(1500),
    "BQBHQK" varchar(6000),
    "QJCS" varchar(6000),
    "SSJCZBM" varchar(75),
    "SSJCZMC" varchar(120),
    "SSJCZMBBWMC" varchar(75),
    "JRWMC" varchar(150),
    "CZFF" varchar(3000),
    "CZCS" numeric,
    "QJKSRQSJ" timestamp,
    "QJJSRQSJ" timestamp,
    "JC_JYXMMC" varchar(750),
    "JC_JYJG" varchar(3000),
    "JC_JYDLJG" varchar(750),
    "JC_JYJGDM" varchar(75),
    "ZYSX" varchar(1500),
    "CJQJRYGHLB" varchar(300),
    "CJQJRYXMLB" varchar(300),
    "CJQJRYZYJS" varchar(45),
    "JLYSGH" varchar(54),
    "JLYSXM" varchar(108),
    "QMRQSJ" timestamp,
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_QJJL" IS '抢救记录';
COMMENT ON COLUMN "TB_CIS_QJJL"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_QJJL"."QJJLLSH" IS '抢救记录流水号';
COMMENT ON COLUMN "TB_CIS_QJJL"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_QJJL"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_QJJL"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_QJJL"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_QJJL"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_QJJL"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_QJJL"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_QJJL"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_QJJL"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_QJJL"."JBZDBM" IS '疾病诊断编码';
COMMENT ON COLUMN "TB_CIS_QJJL"."JBZDMC" IS '疾病诊断名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."BQBHQK" IS '病情变化情况';
COMMENT ON COLUMN "TB_CIS_QJJL"."QJCS" IS '抢救措施';
COMMENT ON COLUMN "TB_CIS_QJJL"."SSJCZBM" IS '手术及操作编码';
COMMENT ON COLUMN "TB_CIS_QJJL"."SSJCZMC" IS '手术及操作名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."SSJCZMBBWMC" IS '手术及操作目标部位名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."JRWMC" IS '介入物名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."CZFF" IS '操作方法';
COMMENT ON COLUMN "TB_CIS_QJJL"."CZCS" IS '操作次数';
COMMENT ON COLUMN "TB_CIS_QJJL"."QJKSRQSJ" IS '抢救开始日期时间';
COMMENT ON COLUMN "TB_CIS_QJJL"."QJJSRQSJ" IS '抢救结束日期时间';
COMMENT ON COLUMN "TB_CIS_QJJL"."JC_JYXMMC" IS '检查/检验项目名称';
COMMENT ON COLUMN "TB_CIS_QJJL"."JC_JYJG" IS '检查/检验结果';
COMMENT ON COLUMN "TB_CIS_QJJL"."JC_JYDLJG" IS '检查/检验定量结果';
COMMENT ON COLUMN "TB_CIS_QJJL"."JC_JYJGDM" IS '检查/检验结果代码';
COMMENT ON COLUMN "TB_CIS_QJJL"."ZYSX" IS '注意事项';
COMMENT ON COLUMN "TB_CIS_QJJL"."CJQJRYGHLB" IS '参加抢救人员工号列表';
COMMENT ON COLUMN "TB_CIS_QJJL"."CJQJRYXMLB" IS '参加抢救人员姓名列表';
COMMENT ON COLUMN "TB_CIS_QJJL"."CJQJRYZYJS" IS '参加抢救人员专业技术职务类别代码';
COMMENT ON COLUMN "TB_CIS_QJJL"."JLYSGH" IS '记录医师编号';
COMMENT ON COLUMN "TB_CIS_QJJL"."JLYSXM" IS '记录医师姓名';
COMMENT ON COLUMN "TB_CIS_QJJL"."QMRQSJ" IS '签名日期时间';
COMMENT ON COLUMN "TB_CIS_QJJL"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_QJJL"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_QJJL"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_QJJL"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_QJJL"."YLYL2" IS '预留二';