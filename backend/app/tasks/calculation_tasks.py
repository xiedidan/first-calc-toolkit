"""
计算任务Celery任务
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
import json

from celery.exceptions import SoftTimeLimitExceeded
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.calculation_step_log import CalculationStepLog
from app.models.department import Department
from app.models.model_node import ModelNode
from app.models.model_version import ModelVersion
from app.models.data_source import DataSource


@celery_app.task(bind=True, max_retries=0, time_limit=3600, soft_time_limit=3500)
def execute_calculation_task(
    self,
    task_id: str,
    model_version_id: int,
    workflow_id: Optional[int],
    department_ids: Optional[List[int]],
    period: str
):
    """执行计算任务
    
    Args:
        task_id: 任务ID
        model_version_id: 模型版本ID
        workflow_id: 计算流程ID
        department_ids: 科室ID列表
        period: 计算周期
        
    Task配置:
        max_retries: 0 - 不自动重试
        time_limit: 3600秒 - 硬超时限制（1小时）
        soft_time_limit: 3500秒 - 软超时限制（58分钟）
    """
    db = SessionLocal()
    task = None
    
    try:
        # 查询并更新任务状态
        task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
        if not task:
            print(f"任务不存在: {task_id}")
            return {"success": False, "error": "任务不存在"}
        
        # 更新为运行中
        task.status = "running"
        task.started_at = datetime.now()
        db.commit()
        print(f"[INFO] 任务 {task_id} 开始执行")
        print(f"[INFO] 参数: model_version_id={model_version_id}, workflow_id={workflow_id}, period={period}")
        print(f"[INFO] department_ids={department_ids}")
        
        # 获取医疗机构ID（从模型版本获取）
        model_version = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
        if not model_version:
            task.status = "failed"
            task.error_message = "模型版本不存在"
            task.completed_at = datetime.now()
            db.commit()
            return {"success": False, "error": "模型版本不存在"}
        
        hospital_id = model_version.hospital_id
        print(f"[INFO] 医疗机构ID: {hospital_id}")
        
        # 获取要计算的科室列表
        if department_ids:
            # 指定了科室：按科室循环执行
            departments = db.query(Department).filter(
                Department.id.in_(department_ids),
                Department.is_active == True
            ).all()
            
            if not departments:
                task.status = "failed"
                task.error_message = "没有需要计算的科室"
                task.completed_at = datetime.now()
                db.commit()
                return {"success": False, "error": "没有需要计算的科室"}
        else:
            # 未指定科室：只执行一次，SQL 自己处理所有科室
            # 创建一个虚拟的科室对象，用于参数替换
            departments = [None]  # None 表示不针对特定科室
        
        total_departments = len(departments)
        
        # 如果指定了workflow_id，使用计算流程
        if workflow_id:
            workflow = db.query(CalculationWorkflow).filter(
                CalculationWorkflow.id == workflow_id
            ).first()
            
            if not workflow:
                task.status = "failed"
                task.error_message = "计算流程不存在"
                task.completed_at = datetime.now()
                db.commit()
                return {"success": False, "error": "计算流程不存在"}
            
            # 获取所有启用的步骤
            steps = db.query(CalculationStep).filter(
                CalculationStep.workflow_id == workflow_id,
                CalculationStep.is_enabled == True
            ).order_by(CalculationStep.sort_order).all()
            
            print(f"[INFO] 找到 {len(steps)} 个启用的步骤")
            print(f"[INFO] 需要处理 {total_departments} 个科室/批次")
            
            # 执行计算流程
            has_failed_step = False
            failed_error = None
            
            for idx, department in enumerate(departments):
                dept_name = department.his_name if department else "全部科室"
                print(f"[INFO] 处理第 {idx+1}/{total_departments} 个: {dept_name}")
                
                try:
                    # 执行所有步骤
                    for step in steps:
                        print(f"[INFO] 执行步骤 {step.id}: {step.name}")
                        execute_calculation_step(
                            db=db,
                            task_id=task_id,
                            step=step,
                            department=department,  # 可能为 None
                            period=period,
                            model_version_id=model_version_id,
                            hospital_id=hospital_id
                        )
                    
                    # 更新进度
                    progress = (idx + 1) / total_departments * 100
                    task.progress = Decimal(str(progress))
                    db.commit()
                    
                    # 更新Celery任务状态
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': idx + 1, 'total': total_departments}
                    )
                    
                except Exception as e:
                    # 任何步骤失败，整个任务标记为失败
                    has_failed_step = True
                    dept_name = department.his_name if department else "全部科室"
                    failed_error = f"科室 {dept_name} 计算失败: {str(e)}"
                    print(f"[ERROR] {failed_error}")
                    import traceback
                    traceback.print_exc()
                    # 不再继续执行后续科室
                    break
            
            # 如果有步骤失败，标记任务为失败
            if has_failed_step:
                print(f"任务 {task_id} 执行失败，更新状态")
                try:
                    db.rollback()  # 先回滚之前可能失败的事务
                    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
                    task.status = "failed"
                    task.error_message = failed_error
                    task.completed_at = datetime.now()
                    db.commit()
                    print(f"任务 {task_id} 状态已更新为失败")
                except Exception as update_error:
                    print(f"[ERROR] 更新任务失败状态时出错: {str(update_error)}")
                return {"success": False, "error": failed_error}
        else:
            # 兼容模式：使用模型节点中的代码
            # TODO: 实现兼容模式
            task.status = "failed"
            task.error_message = "请指定计算流程ID"
            task.completed_at = datetime.now()
            db.commit()
            return {"success": False, "error": "请指定计算流程ID"}
        
        # 计算汇总数据（仅在指定科室时计算）
        if department_ids and departments and departments[0] is not None:
            print(f"任务 {task_id} 开始计算汇总数据")
            calculate_summaries(db, task_id, departments)
        
        # 更新任务状态为完成
        print(f"任务 {task_id} 执行完成，更新状态")
        task.status = "completed"
        task.progress = Decimal("100.00")
        task.completed_at = datetime.now()
        db.commit()
        print(f"任务 {task_id} 状态已更新为完成")
        
        return {"success": True, "message": "计算完成"}
    
    except SoftTimeLimitExceeded:
        # 任务超时
        error_msg = "任务执行超时（超过58分钟）"
        print(f"[ERROR] 任务 {task_id} 超时")
        try:
            db.rollback()  # 先回滚失败的事务
            if not task:
                task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
            if task and task.status != "failed":  # 避免覆盖已经设置的失败状态
                task.status = "failed"
                task.error_message = error_msg
                task.completed_at = datetime.now()
                db.commit()
                print(f"任务 {task_id} 超时状态已更新")
        except Exception as commit_error:
            print(f"[ERROR] 更新任务超时状态失败: {str(commit_error)}")
            import traceback
            traceback.print_exc()
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        # 捕获所有其他异常
        error_msg = str(e)
        print(f"[ERROR] 任务 {task_id} 执行异常: {error_msg}")
        import traceback
        traceback.print_exc()
        
        try:
            db.rollback()  # 先回滚失败的事务
            if not task:
                task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
            if task and task.status != "failed":  # 避免覆盖已经设置的失败状态
                task.status = "failed"
                task.error_message = error_msg
                task.completed_at = datetime.now()
                db.commit()
                print(f"任务 {task_id} 失败状态已更新")
        except Exception as commit_error:
            print(f"[ERROR] 更新任务失败状态时出错: {str(commit_error)}")
            import traceback
            traceback.print_exc()
        
        return {"success": False, "error": error_msg}
        
    finally:
        try:
            db.close()
        except Exception:
            pass


def execute_calculation_step(
    db: Session,
    task_id: str,
    step: CalculationStep,
    department: Optional[Department],
    period: str,
    model_version_id: int,
    hospital_id: int
):
    """执行单个计算步骤
    
    Args:
        db: 数据库会话
        task_id: 任务ID
        step: 计算步骤
        department: 科室对象，如果为 None 表示不针对特定科室（批量处理模式）
        period: 计算周期
        model_version_id: 模型版本ID
        hospital_id: 医疗机构ID
    """
    start_time = datetime.now()
    
    try:
        # 替换占位符
        code = step.code_content
        
        # 基础参数
        code = code.replace("{current_year_month}", period)
        code = code.replace("{period}", period)  # 别名
        code = code.replace("{year_month}", period)  # 导向调整步骤使用
        
        # 科室相关参数
        if department:
            # 指定了科室：使用具体科室的信息
            code = code.replace("{hospital_id}", str(department.hospital_id))
            code = code.replace("{department_id}", str(department.id))
            code = code.replace("{department_code}", department.his_code or "")
            code = code.replace("{department_name}", department.his_name or "")
            code = code.replace("{cost_center_code}", department.cost_center_code or "")
            code = code.replace("{cost_center_name}", department.cost_center_name or "")
            code = code.replace("{accounting_unit_code}", department.accounting_unit_code or "")
            code = code.replace("{accounting_unit_name}", department.accounting_unit_name or "")
        else:
            # 未指定科室：批量处理模式，使用传入的hospital_id
            code = code.replace("{hospital_id}", str(hospital_id))
            code = code.replace("{department_id}", "NULL")
            code = code.replace("{department_code}", "")
            code = code.replace("{department_name}", "")
            code = code.replace("{cost_center_code}", "")
            code = code.replace("{cost_center_name}", "")
            code = code.replace("{accounting_unit_code}", "")
            code = code.replace("{accounting_unit_name}", "")
        
        # 日期相关参数（从 period 计算）
        # period 格式: YYYY-MM
        year, month = period.split("-")
        code = code.replace("{year}", year)
        code = code.replace("{month}", month)
        
        # 计算月份的第一天和最后一天
        from calendar import monthrange
        last_day = monthrange(int(year), int(month))[1]
        start_date = f"{period}-01"
        end_date = f"{period}-{last_day:02d}"
        code = code.replace("{start_date}", start_date)
        code = code.replace("{end_date}", end_date)
        
        # 任务相关参数
        code = code.replace("{task_id}", task_id)
        code = code.replace("{version_id}", str(model_version_id))
        
        result_data = {}
        
        # 执行代码
        if step.code_type == "sql":
            # 执行SQL代码
            if not step.data_source_id:
                raise ValueError(f"SQL步骤 '{step.name}' 必须指定数据源，请在前端编辑步骤并选择数据源")
            
            # 获取数据源
            data_source = db.query(DataSource).filter(DataSource.id == step.data_source_id).first()
            if not data_source:
                raise ValueError(f"数据源不存在: {step.data_source_id}")
            
            print(f"[DEBUG] 步骤 {step.id} 使用数据源: {data_source.name} (ID: {data_source.id})")
            
            # 获取或创建连接池
            from app.services.data_source_service import connection_manager
            
            pool = connection_manager.get_pool(data_source.id)
            if not pool:
                print(f"[DEBUG] 创建新的连接池: {data_source.name}")
                pool = connection_manager.create_pool(data_source)
            
            # 执行SQL
            print(f"[DEBUG] 开始执行SQL，task_id={task_id}")
            print(f"[DEBUG] 步骤名称: {step.name}")
            print(f"[DEBUG] SQL模板前100字符: {code[:100]}...")
            print(f"[DEBUG] SQL模板包含'cr.weight': {'cr.weight' in code}")
            print(f"[DEBUG] SQL模板包含'ms.weight': {'ms.weight' in code}")
            with pool.connect() as connection:
                # 分割多个SQL语句（以分号分隔）
                statements = []
                for s in code.split(';'):
                    s = s.strip()
                    if not s:
                        continue
                    # 过滤掉纯注释的语句
                    lines = [line.strip() for line in s.split('\n') if line.strip() and not line.strip().startswith('--')]
                    if lines:
                        statements.append(s)
                
                last_result = None
                total_affected = 0
                
                for statement in statements:
                    result = connection.execute(text(statement))
                    last_result = result
                    
                    # 如果是DML语句，累计影响行数
                    if hasattr(result, 'rowcount') and result.rowcount > 0:
                        total_affected += result.rowcount
                
                # 提交事务
                print(f"[DEBUG] 提交事务，共执行 {len(statements)} 个语句，影响 {total_affected} 行")
                connection.commit()
                print(f"[DEBUG] 事务提交成功")
                
                # 处理最后一个语句的结果
                if last_result and last_result.returns_rows:
                    columns = list(last_result.keys())
                    rows = []
                    for row in last_result.fetchall():
                        row_dict = {}
                        for key, value in row._mapping.items():
                            # 将 datetime 对象转换为字符串
                            if isinstance(value, datetime):
                                row_dict[key] = value.isoformat()
                            elif isinstance(value, Decimal):
                                row_dict[key] = float(value)
                            else:
                                row_dict[key] = value
                        rows.append(row_dict)
                    
                    result_data = {
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows),
                        "total_affected": total_affected
                    }
                else:
                    # DDL/DML 语句
                    result_data = {
                        "message": "SQL执行成功",
                        "affected_rows": total_affected,
                        "statements_executed": len(statements)
                    }
                    
        elif step.code_type == "python":
            # Python代码执行（暂未实现）
            raise ValueError("Python步骤暂未实现")
        else:
            raise ValueError(f"不支持的代码类型: {step.code_type}")
        
        # 记录步骤日志
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 生成执行信息
        execution_info = f"执行成功"
        if result_data.get("row_count"):
            execution_info += f"，返回 {result_data['row_count']} 行数据"
        elif result_data.get("affected_rows"):
            execution_info += f"，影响 {result_data['affected_rows']} 行"
        
        try:
            log = CalculationStepLog(
                task_id=task_id,
                step_id=step.id,
                department_id=department.id if department else None,  # 批量模式时为 None
                status="success",
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                result_data=result_data,
                execution_info=execution_info
            )
            db.add(log)
            db.commit()
            dept_name = department.his_name if department else "全部科室"
            print(f"步骤 {step.id} ({step.name}) 在科室 {dept_name} 执行成功，耗时 {duration_ms}ms")
        except Exception as log_error:
            db.rollback()  # 回滚失败的事务
            print(f"[ERROR] 记录步骤成功日志时出错: {str(log_error)}")
            import traceback
            traceback.print_exc()
            # 日志记录失败不应该影响任务执行，所以不抛出异常
        
    except Exception as e:
        # 记录错误日志
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        error_msg = str(e)
        dept_name = department.his_name if department else "全部科室"
        print(f"[ERROR] 步骤 {step.id} ({step.name}) 在科室 {dept_name} 执行失败: {error_msg}")
        
        try:
            log = CalculationStepLog(
                task_id=task_id,
                step_id=step.id,
                department_id=department.id if department else None,  # 批量模式时为 None
                status="failed",
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                execution_info=f"执行失败: {error_msg}"
            )
            db.add(log)
            db.commit()
            print(f"步骤 {step.id} 失败日志已记录")
        except Exception as log_error:
            db.rollback()  # 回滚失败的事务
            print(f"[ERROR] 记录步骤失败日志时出错: {str(log_error)}")
            import traceback
            traceback.print_exc()
        
        # 重新抛出异常，让上层处理
        raise


def calculate_summaries(db: Session, task_id: str, departments: List[Department]):
    """计算汇总数据"""
    for department in departments:
        # 查询该科室的所有序列结果
        results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == department.id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        # 计算各序列的价值
        doctor_value = Decimal("0")
        nurse_value = Decimal("0")
        tech_value = Decimal("0")
        
        for result in results:
            if "医生" in result.node_name:
                doctor_value += result.value or Decimal("0")
            elif "护理" in result.node_name:
                nurse_value += result.value or Decimal("0")
            elif "医技" in result.node_name:
                tech_value += result.value or Decimal("0")
        
        total_value = doctor_value + nurse_value + tech_value
        
        # 计算占比
        doctor_ratio = doctor_value / total_value * 100 if total_value > 0 else Decimal("0")
        nurse_ratio = nurse_value / total_value * 100 if total_value > 0 else Decimal("0")
        tech_ratio = tech_value / total_value * 100 if total_value > 0 else Decimal("0")
        
        # 创建汇总记录
        summary = CalculationSummary(
            task_id=task_id,
            department_id=department.id,
            doctor_value=doctor_value,
            doctor_ratio=doctor_ratio,
            nurse_value=nurse_value,
            nurse_ratio=nurse_ratio,
            tech_value=tech_value,
            tech_ratio=tech_ratio,
            total_value=total_value
        )
        db.add(summary)
    
    db.commit()
