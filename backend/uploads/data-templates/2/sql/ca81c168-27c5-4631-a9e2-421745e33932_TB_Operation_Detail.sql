DROP TABLE IF EXISTS "TB_Operation_Detail";
CREATE TABLE "TB_Operation_Detail" (
    "YLJGDM" varchar(33),
    "SSMXLSH" varchar(75),
    "SQDH" varchar(96),
    "SSID" varchar(75),
    "BRZSY" varchar(96),
    "JZLSH" varchar(75),
    "MZZYBZ" varchar(3),
    "RJSSBZ" varchar(3),
    "SSLX" varchar(3),
    "SSCZBM" varchar(75),
    "SSCZMC" varchar(96),
    "SSQZD" varchar(150),
    "SSHZD" varchar(150),
    "SSKSSJ" timestamp,
    "SSJSSJ" timestamp,
    "SSJB" varchar(3),
    "SSYSGH" varchar(54),
    "SSYSXM" varchar(108),
    "SSYSZ1GH" varchar(54),
    "SSYSZ1XM" varchar(108),
    "SSYSZ2GH" varchar(54),
    "SSYSZ2XM" varchar(108),
    "MZYSGH" varchar(54),
    "MZYSXM" varchar(108),
    "MZFF" varchar(75),
    "MZFS" varchar(3),
    "QKYHDJ" varchar(2),
    "QTYXCZ" varchar(3000),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_Operation_Detail" IS '手术明细表';
COMMENT ON COLUMN "TB_Operation_Detail"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_Operation_Detail"."SSMXLSH" IS '手术明细流水号';
COMMENT ON COLUMN "TB_Operation_Detail"."SQDH" IS '申请单号';
COMMENT ON COLUMN "TB_Operation_Detail"."SSID" IS '手术 ID';
COMMENT ON COLUMN "TB_Operation_Detail"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_Operation_Detail"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_Operation_Detail"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_Operation_Detail"."RJSSBZ" IS '日间手术标志';
COMMENT ON COLUMN "TB_Operation_Detail"."SSLX" IS '手术类型';
COMMENT ON COLUMN "TB_Operation_Detail"."SSCZBM" IS '手术操作编码';
COMMENT ON COLUMN "TB_Operation_Detail"."SSCZMC" IS '手术操作名称';
COMMENT ON COLUMN "TB_Operation_Detail"."SSQZD" IS '手术前诊断';
COMMENT ON COLUMN "TB_Operation_Detail"."SSHZD" IS '手术后诊断';
COMMENT ON COLUMN "TB_Operation_Detail"."SSKSSJ" IS '手术起始时间';
COMMENT ON COLUMN "TB_Operation_Detail"."SSJSSJ" IS '手术结束时间';
COMMENT ON COLUMN "TB_Operation_Detail"."SSJB" IS '手术级别';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSGH" IS '手术医生编号';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSXM" IS '手术医生姓名';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSZ1GH" IS '手术医生 I 助编号';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSZ1XM" IS '手术医生 I 助姓名';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSZ2GH" IS '手术医生 II 助编号';
COMMENT ON COLUMN "TB_Operation_Detail"."SSYSZ2XM" IS '手术医生 II 助姓名';
COMMENT ON COLUMN "TB_Operation_Detail"."MZYSGH" IS '麻醉医师编号';
COMMENT ON COLUMN "TB_Operation_Detail"."MZYSXM" IS '麻醉医师姓名';
COMMENT ON COLUMN "TB_Operation_Detail"."MZFF" IS '麻醉-方法';
COMMENT ON COLUMN "TB_Operation_Detail"."MZFS" IS '麻醉方式编码';
COMMENT ON COLUMN "TB_Operation_Detail"."QKYHDJ" IS '切口愈合等级编码';
COMMENT ON COLUMN "TB_Operation_Detail"."QTYXCZ" IS '其他医学处置';
COMMENT ON COLUMN "TB_Operation_Detail"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_Operation_Detail"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_Operation_Detail"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_Operation_Detail"."YLYL2" IS '预留二';