DROP TABLE IF EXISTS "TB_IN_CPATH";
CREATE TABLE "TB_IN_CPATH" (
    "ZXLJBH" varchar(75),
    "YLJGDM" varchar(33),
    "LJZTDM" varchar(2),
    "LCLJMC" varchar(15),
    "YWSJ" timestamp,
    "JZLSH" varchar(75),
    "BRZSY" varchar(96),
    "CISID" varchar(27),
    "ZYBAH" varchar(27),
    "ZSKBH" varchar(15),
    "YXBZ" varchar(2),
    "KSDM" varchar(23),
    "KSMC" varchar(75),
    "RZZDBM" varchar(96),
    "RZZDMC" varchar(768),
    "BYZDDM" varchar(96),
    "BYZDMC" varchar(768),
    "BYZDSJ" timestamp,
    "BZMC" numeric(15,4),
    "LJBM" varchar(15),
    "LJMC" varchar(150),
    "BYYYDM" varchar(3),
    "JLSJ" timestamp,
    "ZRHSXM" varchar(75),
    "ZZYSGH" varchar(27),
    "ZZYSXM" varchar(75),
    "ZYYSGH" varchar(27),
    "ZYYSXM" varchar(75),
    "JLRYBM" varchar(27),
    "JLRXM" varchar(75),
    "TCYY" varchar(150),
    "BZSM" varchar(750),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_IN_CPATH" IS '临床路径执行路径记录表';
COMMENT ON COLUMN "TB_IN_CPATH"."ZXLJBH" IS '执行路径编号';
COMMENT ON COLUMN "TB_IN_CPATH"."YLJGDM" IS '医疗机构组织机构代码';
COMMENT ON COLUMN "TB_IN_CPATH"."LJZTDM" IS '路径状态代码';
COMMENT ON COLUMN "TB_IN_CPATH"."LCLJMC" IS '路径状态名称';
COMMENT ON COLUMN "TB_IN_CPATH"."YWSJ" IS '业务发生日期时间';
COMMENT ON COLUMN "TB_IN_CPATH"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_IN_CPATH"."BRZSY" IS '患者主索引';
COMMENT ON COLUMN "TB_IN_CPATH"."CISID" IS '住院号';
COMMENT ON COLUMN "TB_IN_CPATH"."ZYBAH" IS '住院病案号';
COMMENT ON COLUMN "TB_IN_CPATH"."ZSKBH" IS '路径模板名称';
COMMENT ON COLUMN "TB_IN_CPATH"."YXBZ" IS '有效标志';
COMMENT ON COLUMN "TB_IN_CPATH"."KSDM" IS '科室代码';
COMMENT ON COLUMN "TB_IN_CPATH"."KSMC" IS '科室名称';
COMMENT ON COLUMN "TB_IN_CPATH"."RZZDBM" IS '入径诊断编码';
COMMENT ON COLUMN "TB_IN_CPATH"."RZZDMC" IS '入径诊断名称';
COMMENT ON COLUMN "TB_IN_CPATH"."BYZDDM" IS '变异诊断代码';
COMMENT ON COLUMN "TB_IN_CPATH"."BYZDMC" IS '变异诊断名称';
COMMENT ON COLUMN "TB_IN_CPATH"."BYZDSJ" IS '变异诊断时间';
COMMENT ON COLUMN "TB_IN_CPATH"."BZMC" IS '总费用';
COMMENT ON COLUMN "TB_IN_CPATH"."LJBM" IS '路径编码';
COMMENT ON COLUMN "TB_IN_CPATH"."LJMC" IS '路径名称';
COMMENT ON COLUMN "TB_IN_CPATH"."BYYYDM" IS '变异原因代码';
COMMENT ON COLUMN "TB_IN_CPATH"."JLSJ" IS '记录日期时间';
COMMENT ON COLUMN "TB_IN_CPATH"."ZRHSXM" IS '责任护士姓名';
COMMENT ON COLUMN "TB_IN_CPATH"."ZZYSGH" IS '主治医师工号';
COMMENT ON COLUMN "TB_IN_CPATH"."ZZYSXM" IS '主治医师姓名';
COMMENT ON COLUMN "TB_IN_CPATH"."ZYYSGH" IS '住院医师工号';
COMMENT ON COLUMN "TB_IN_CPATH"."ZYYSXM" IS '住院医师姓名';
COMMENT ON COLUMN "TB_IN_CPATH"."JLRYBM" IS '记录人工号';
COMMENT ON COLUMN "TB_IN_CPATH"."JLRXM" IS '记录人姓名';
COMMENT ON COLUMN "TB_IN_CPATH"."TCYY" IS '退出原因';
COMMENT ON COLUMN "TB_IN_CPATH"."BZSM" IS '备注说明';
COMMENT ON COLUMN "TB_IN_CPATH"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_IN_CPATH"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_IN_CPATH"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_IN_CPATH"."YLYL2" IS '预留二';