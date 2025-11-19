DROP TABLE IF EXISTS "TB_MZ_CFZB";
CREATE TABLE "TB_MZ_CFZB" (
    "YLJGDM" varchar(33),
    "CFZID" varchar(54),
    "BRZSY" varchar(96),
    "JZLSH" varchar(54),
    "CFDL" varchar(6),
    "CFLX" varchar(3),
    "CFHM" varchar(96),
    "JZKSDM" varchar(96),
    "JZKSMC" varchar(114),
    "KFYSGH" varchar(48),
    "KFYSXM" varchar(108),
    "KFYSSFZHM" varchar(27),
    "KFRQ" timestamp,
    "HZBSH" varchar(54),
    "HZXM" varchar(108),
    "HZXB" varchar(6),
    "HZNL" varchar(15),
    "HZTZ" numeric(4,1),
    "FB" varchar(15),
    "XYZDDM" varchar(750),
    "LCZD" varchar(300),
    "ZYBMDM" varchar(150),
    "ZYBMMC" varchar(750),
    "ZYZHDM" varchar(150),
    "ZYZHMC" varchar(750),
    "CFJE" numeric(10,4),
    "CFYXTS" numeric(2),
    "CFBZXX" varchar(150),
    "ZZZF" varchar(750),
    "CFSHYJSBH" varchar(54),
    "CFSHYJSQM" varchar(108),
    "CFSHYJSSFZHM" varchar(27),
    "CFTPYJSBH" varchar(54),
    "CFTPYJSQM" varchar(108),
    "CFTPYJSSFZHM" varchar(27),
    "CFFYYJSBH" varchar(54),
    "CFFYYJSQM" varchar(108),
    "CFFYYJSSFZHM" varchar(27),
    "CFHDYJSBH" varchar(54),
    "CFHDYJSQM" varchar(108),
    "CFHDYJSSFZHM" varchar(27),
    "ZYYPJSJ" numeric(2),
    "ZYJZPC" varchar(150),
    "ZYYPJZF" varchar(150),
    "ZYYPFF" varchar(150),
    "ZYYYFF" varchar(150),
    "ZYYPCF" varchar(750),
    "CFDPSJ" timestamp,
    "CFDPJG" varchar(750),
    "BZ" varchar(75),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_MZ_CFZB" IS '门诊处方主表';
COMMENT ON COLUMN "TB_MZ_CFZB"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFZID" IS '处方主 ID';
COMMENT ON COLUMN "TB_MZ_CFZB"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_MZ_CFZB"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFDL" IS '处方大类';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFLX" IS '处方类型';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFHM" IS '处方号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."JZKSDM" IS '开方科室代码';
COMMENT ON COLUMN "TB_MZ_CFZB"."JZKSMC" IS '开方科室名称';
COMMENT ON COLUMN "TB_MZ_CFZB"."KFYSGH" IS '开方医生编号';
COMMENT ON COLUMN "TB_MZ_CFZB"."KFYSXM" IS '开方医生姓名';
COMMENT ON COLUMN "TB_MZ_CFZB"."KFYSSFZHM" IS '开方医生身份证号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."KFRQ" IS '开方时间';
COMMENT ON COLUMN "TB_MZ_CFZB"."HZBSH" IS '患者标识号';
COMMENT ON COLUMN "TB_MZ_CFZB"."HZXM" IS '患者姓名';
COMMENT ON COLUMN "TB_MZ_CFZB"."HZXB" IS '患者性别';
COMMENT ON COLUMN "TB_MZ_CFZB"."HZNL" IS '患者年龄';
COMMENT ON COLUMN "TB_MZ_CFZB"."HZTZ" IS '患者体重';
COMMENT ON COLUMN "TB_MZ_CFZB"."FB" IS '费别';
COMMENT ON COLUMN "TB_MZ_CFZB"."XYZDDM" IS '西医诊断代码';
COMMENT ON COLUMN "TB_MZ_CFZB"."LCZD" IS '西医临床诊断';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYBMDM" IS '中医病名代码';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYBMMC" IS '中医病名名称';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYZHDM" IS '中医证候代码';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYZHMC" IS '中医证候名称';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFJE" IS '处方金额';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFYXTS" IS '处方有效天数';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFBZXX" IS '处方说明信息';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZZZF" IS '治则治法';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFSHYJSBH" IS '处方审核药剂师编号';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFSHYJSQM" IS '处方审核药剂师签名';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFSHYJSSFZHM" IS '处方审核药剂师身份证号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFTPYJSBH" IS '处方调配药剂师编号';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFTPYJSQM" IS '处方调配药剂师签名';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFTPYJSSFZHM" IS '处方调配药剂师身份证号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFFYYJSBH" IS '处方发药药剂师编号';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFFYYJSQM" IS '处方发药药剂师签名';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFFYYJSSFZHM" IS '处方发药药剂师身份证号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFHDYJSBH" IS '处方核对药剂师编号';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFHDYJSQM" IS '处方核对药剂师签名';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFHDYJSSFZHM" IS '处方核对药剂师身份证号码';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYYPJSJ" IS '中药饮片剂数';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYJZPC" IS '中药饮片煎煮频次';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYYPJZF" IS '中药饮片煎煮法';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYYPFF" IS '中药饮片服法';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYYYFF" IS '中药饮片用药方法';
COMMENT ON COLUMN "TB_MZ_CFZB"."ZYYPCF" IS '中药饮片处方';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFDPSJ" IS '处方点评时间';
COMMENT ON COLUMN "TB_MZ_CFZB"."CFDPJG" IS '处方点评结果';
COMMENT ON COLUMN "TB_MZ_CFZB"."BZ" IS '说明';
COMMENT ON COLUMN "TB_MZ_CFZB"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_MZ_CFZB"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_MZ_CFZB"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_MZ_CFZB"."YLYL2" IS '预留二';