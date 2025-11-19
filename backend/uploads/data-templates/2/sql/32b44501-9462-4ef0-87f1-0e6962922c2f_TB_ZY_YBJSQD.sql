DROP TABLE IF EXISTS "TB_ZY_YBJSQD";
CREATE TABLE "TB_ZY_YBJSQD" (
    "YLJGDM" varchar(33),
    "DDYLJGDM" varchar(30),
    "YBQDJSLSH" varchar(14),
    "BRZSY" varchar(96),
    "BAH" varchar(48),
    "JZLSH" varchar(54),
    "YBKKH" varchar(45),
    "YBJSDJ" varchar(9),
    "SBSJ" timestamp,
    "YBLX" varchar(2),
    "TSRYLX" varchar(75),
    "XSRRYLX" varchar(2),
    "RYSJ" timestamp,
    "CBD" varchar(225),
    "BZDM" varchar(3000),
    "BZMC" varchar(3000),
    "SSJCZDM" varchar(3000),
    "SSJCZMC" varchar(3000),
    "YBFPDH" varchar(75),
    "YBFPHM" varchar(75),
    "YBJSQSSJ" timestamp,
    "YBJSZZSJ" timestamp,
    "YBZFFS" varchar(3),
    "ZJE" numeric(12,4),
    "YBTCJJZFJE" numeric(12,4),
    "ZGDEBZ" numeric(12,4),
    "JMDBBX" numeric(12,4),
    "GWYYLBZ" numeric(12,4),
    "YLJZZFJE" numeric(12,4),
    "QTZFQYBC" numeric(12,4),
    "QTZFSYBX" numeric(12,4),
    "GRZHZFJE" numeric(12,4),
    "GRXJZFJE" numeric(12,4),
    "GRZFJE" numeric(12,4),
    "GRYBZFJE" numeric(12,4),
    "ZYYLLB" varchar(3),
    "ZLLB" varchar(6),
    "HXJSYJS" varchar(30),
    "ZZJHBFLX" varchar(3000),
    "JCZZJHSSJ" varchar(3000),
    "SXJL" varchar(6000),
    "TJHLTS" numeric(4),
    "YJHLTS" numeric(4),
    "EJHLTS" numeric(4),
    "SJHLTS" numeric(4),
    "CYSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_ZY_YBJSQD" IS '医保结算清单';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."DDYLJGDM" IS '定点医疗机构代码';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBQDJSLSH" IS '医保结算清单号';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."BAH" IS '病案号（住院号）';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBKKH" IS '医保卡号';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBJSDJ" IS '医保结算等级';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."SBSJ" IS '申报时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBLX" IS '医保类型';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."TSRYLX" IS '特殊人员类型';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."XSRRYLX" IS '新生儿入院类型';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."RYSJ" IS '入院时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."CBD" IS '参保地';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."BZDM" IS '病种代码';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."BZMC" IS '病种名称';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."SSJCZDM" IS '手术及操作代码';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."SSJCZMC" IS '手术及操作名称';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBFPDH" IS '医保发票代号';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBFPHM" IS '医保发票号码';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBJSQSSJ" IS '医保结算起始时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBJSZZSJ" IS '医保结算终止时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBZFFS" IS '医保支付方式';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."ZJE" IS '总金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YBTCJJZFJE" IS '医保统筹基金支付金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."ZGDEBZ" IS '补充医疗保险支付—职工大额补助';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."JMDBBX" IS '补充医疗保险支付—居民大病保险';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."GWYYLBZ" IS '补充医疗保险支付—公务员医疗补助';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YLJZZFJE" IS '医疗救助支付金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."QTZFQYBC" IS '其他支付—企业补充';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."QTZFSYBX" IS '其他支付—商业保险';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."GRZHZFJE" IS '个人帐户支付金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."GRXJZFJE" IS '个人现金支付金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."GRZFJE" IS '个人负担—个人自费金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."GRYBZFJE" IS '个人负担—个人医保自付金额';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."ZYYLLB" IS '住院医疗类别';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."ZLLB" IS '治疗类别';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."HXJSYJS" IS '呼吸机使用时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."ZZJHBFLX" IS '重症监护病房类型';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."JCZZJHSSJ" IS '进出重症监护室时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."SXJL" IS '输血记录';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."TJHLTS" IS '特级护理天数';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YJHLTS" IS '一级护理天数';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."EJHLTS" IS '二级护理天数';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."SJHLTS" IS '三级护理天数';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."CYSJ" IS '出院时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_ZY_YBJSQD"."YLYL2" IS '预留二';