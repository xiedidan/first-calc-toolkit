DROP TABLE IF EXISTS "TB_HIS_Opr_Rec";
CREATE TABLE "TB_HIS_Opr_Rec" (
    "YLJGDM" varchar(33),
    "SSID" varchar(75),
    "JZLSH" varchar(75),
    "MZZYBZ" varchar(3),
    "SQRYGH" varchar(54),
    "SQRYXM" varchar(108),
    "DJRYGH" varchar(54),
    "DJRYXM" varchar(108),
    "SQKSDM" varchar(96),
    "SQKSMC" varchar(114),
    "SSKS" varchar(96),
    "SSKSMC" varchar(114),
    "SQYSGH" varchar(54),
    "SQYSXM" varchar(108),
    "SQYSSFZHM" varchar(27),
    "SSYSGH" varchar(54),
    "SSYSXM" varchar(108),
    "SSYSSFZHM" varchar(27),
    "SSNR" varchar(75),
    "SSCZMBBW" varchar(6),
    "SSSQRQ" timestamp,
    "SSYYRQ" timestamp,
    "SSRQ" timestamp,
    "MZSSBZ" varchar(2),
    "RJSSBZ" varchar(2),
    "QKDJ" varchar(15),
    "TBRQ" timestamp,
    "XGBZ" varchar(2),
    "YLYL1" varchar(192),
    "YLYL2" varchar(192)
);
COMMENT ON TABLE "TB_HIS_Opr_Rec" IS '手术记录表';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."YLJGDM" IS '医疗机构代码';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSID" IS '手术 ID';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."JZLSH" IS '就诊流水号';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."MZZYBZ" IS '门诊/住院标志';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQRYGH" IS '申请人员编号';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQRYXM" IS '申请人员姓名';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."DJRYGH" IS '登记人员编号';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."DJRYXM" IS '登记人员姓名';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQKSDM" IS '申请科室代码';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQKSMC" IS '申请科室名称';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSKS" IS '手术科室';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSKSMC" IS '手术科室名称';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQYSGH" IS '申请医生编号';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQYSXM" IS '申请医生姓名';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SQYSSFZHM" IS '申请医生身份证号码';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSYSGH" IS '手术医生编号';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSYSXM" IS '手术医生姓名';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSYSSFZHM" IS '手术医生身份证号码';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSNR" IS '手术内容';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSCZMBBW" IS '手术/操作-目标部位';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSSQRQ" IS '手术申请日期';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSYYRQ" IS '手术预约日期';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."SSRQ" IS '手术日期';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."MZSSBZ" IS '门诊手术标志';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."RJSSBZ" IS '日间手术标志';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."QKDJ" IS '切口等级';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."TBRQ" IS '数据上传时间';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."XGBZ" IS '修改标志';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."YLYL1" IS '预留一';
COMMENT ON COLUMN "TB_HIS_Opr_Rec"."YLYL2" IS '预留二';