DROP TABLE IF EXISTS "TB_CIS_RYJLB";
CREATE TABLE "TB_CIS_RYJLB" (
    "YLJGDM" varchar(33),
    "RYJLLSH" varchar(96),
    "JZLSH" varchar(96),
    "ZYH" varchar(27),
    "BRZSY" varchar(96),
    "NLS" numeric,
    "NLY" varchar(12),
    "NLH" varchar(48),
    "BQMC" varchar(108),
    "KSMC" varchar(108),
    "KSDM" varchar(54),
    "BFH" varchar(15),
    "BCH" varchar(15),
    "RYRQSJ" timestamp,
    "BSCSZXM" varchar(108),
    "CSZYHZDGXD" varchar(3),
    "CSNRKKBZ" varchar(2),
    "ZS" varchar(3000),
    "XBS" varchar(3000),
    "YBJKZKBZ" varchar(2),
    "JBSHWS" varchar(1500),
    "HZCRXBZ" varchar(2),
    "CRBS" varchar(1500),
    "YFJZS" varchar(1500),
    "SSS" varchar(1500),
    "SXS" varchar(1500),
    "GMS" varchar(1500),
    "GRS" varchar(1500),
    "HYS" varchar(1500),
    "YJS" varchar(1500),
    "JZS" varchar(1500),
    "JWS" varchar(1500),
    "TGJC" varchar(3000),
    "TGJC_TW" numeric,
    "TGJC_ML" numeric,
    "TGJC_HXPL" numeric,
    "TGJC_SSY" numeric,
    "TGJC_SZY" numeric,
    "TGJC_SG" numeric,
    "TGJC_TZ" numeric,
    "ZKQK" varchar(1500),
    "FZJCJG" varchar(6000),
    "CBZD_XYZDBM" varchar(750),
    "CBZD_XYZDMC" varchar(1500),
    "CBZD_ZYBMDM" varchar(750),
    "CBZD_ZYBMMC" varchar(1500),
    "CBZD_ZYZHDM" varchar(750),
    "CBZD_ZYZHMC" varchar(1500),
    "CBZDRQ" timestamp,
    "XZZD_XYZDBM" varchar(750),
    "XZZD_XYZDMC" varchar(1500),
    "XZZD_ZYBMDM" varchar(750),
    "BCZD_ZYBMDM" varchar(750),
    "BCZD_ZYBMMC" varchar(1500),
    "BCZD_ZYZHDM" varchar(750),
    "BCZD_ZYZHMC" varchar(1500),
    "BCZDRQ" timestamp,
    "ZZYSZDRQ" timestamp,
    "JZYSGH" varchar(54),
    "JZYSXM" varchar(108),
    "ZYYSGH" varchar(54),
    "ZYYSXM" varchar(108),
    "ZZYSGH" varchar(54),
    "ZZYSXM" varchar(108),
    "ZRYSGH" varchar(54),
    "ZRYSXM" varchar(108),
    "ZYSZGCJG" varchar(1500),
    "ZZZF" varchar(150),
    "QTYXCZ" varchar(3000),
    "BLSXSJ" timestamp,
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_CIS_RYJLB" IS '入院记录表';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."RYJLLSH" IS '入院记录流水号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JZLSH" IS '住院就诊流水号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZYH" IS '住院号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_CIS_RYJLB"."NLS" IS '年龄（岁）';
COMMENT ON COLUMN "TB_CIS_RYJLB"."NLY" IS '年龄（月）';
COMMENT ON COLUMN "TB_CIS_RYJLB"."NLH" IS '年龄（小时）';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BQMC" IS '病区名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BFH" IS '病房号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCH" IS '病床号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."RYRQSJ" IS '入院日期时间';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BSCSZXM" IS '病史陈述者姓名';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CSZYHZDGXD" IS '陈述者与患者的关系代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CSNRKKBZ" IS '陈述内容可靠标志';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZS" IS '主诉';
COMMENT ON COLUMN "TB_CIS_RYJLB"."XBS" IS '现病史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YBJKZKBZ" IS '一般健康状况标志';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JBSHWS" IS '疾病史(含外伤）';
COMMENT ON COLUMN "TB_CIS_RYJLB"."HZCRXBZ" IS '患者传染性标志';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CRBS" IS '传染病史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YFJZS" IS '预防接种史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."SSS" IS '手术史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."SXS" IS '输血史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."GMS" IS '过敏史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."GRS" IS '个人史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."HYS" IS '婚育史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YJS" IS '月经史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JZS" IS '家族史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JWS" IS '既往史';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC" IS '体格检查';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_TW" IS '体格检查-体温';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_ML" IS '体格检查-脉率';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_HXPL" IS '体格检查-呼吸频率';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_SSY" IS '体格检查-收缩压';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_SZY" IS '体格检查-舒张压';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_SG" IS '体格检查-身高';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TGJC_TZ" IS '体格检查-体重';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZKQK" IS '专科情况';
COMMENT ON COLUMN "TB_CIS_RYJLB"."FZJCJG" IS '辅助检查结果';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_XYZDBM" IS '初步诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_XYZDMC" IS '初步诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_ZYBMDM" IS '初步诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_ZYBMMC" IS '初步诊断-中医病名名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_ZYZHDM" IS '初步诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZD_ZYZHMC" IS '初步诊断-中医证候名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."CBZDRQ" IS '初步诊断日期';
COMMENT ON COLUMN "TB_CIS_RYJLB"."XZZD_XYZDBM" IS '修正诊断-西医诊断编码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."XZZD_XYZDMC" IS '修正诊断-西医诊断名称';
COMMENT ON COLUMN "TB_CIS_RYJLB"."XZZD_ZYBMDM" IS '修正诊断-中医病名代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCZD_ZYBMDM" IS '补充诊断-中医病名代码列表';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCZD_ZYBMMC" IS '补充诊断-中医病名名称列表';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCZD_ZYZHDM" IS '补充诊断-中医证候代码';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCZD_ZYZHMC" IS '补充诊断-中医证候名称列表';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BCZDRQ" IS '补充诊断日期';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZZYSZDRQ" IS '主治医师诊断日期';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JZYSGH" IS '接诊医师编号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."JZYSXM" IS '接诊医师姓名';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZYYSGH" IS '住院医师编号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZZYSGH" IS '主治医师编号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZRYSGH" IS '主任医师编号';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZRYSXM" IS '主任医师姓名';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZYSZGCJG" IS '中医"四诊"观察结果';
COMMENT ON COLUMN "TB_CIS_RYJLB"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_CIS_RYJLB"."QTYXCZ" IS '其他医学处置';
COMMENT ON COLUMN "TB_CIS_RYJLB"."BLSXSJ" IS '病历书写时间';
COMMENT ON COLUMN "TB_CIS_RYJLB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_CIS_RYJLB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_CIS_RYJLB"."YLYL2" IS '预留二';